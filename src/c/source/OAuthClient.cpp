#include "../include/OAuthClient.h"
#include <iostream>
#include <sstream>
#include <random>
#include <algorithm>
#include <iomanip>
#include <regex>
#include <json/json.h>

#ifdef _WIN32
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#else
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>
#include <curl/curl.h>
#endif

// Constructor
OAuthClient::OAuthClient(const OAuthConfig& config) : config_(config) {
    // Load existing tokens if available
    loadStoredTokens();
}

// Destructor
OAuthClient::~OAuthClient() {
    stopLocalServer();
}

// Generate PKCE code verifier and challenge
void OAuthClient::generatePKCEPair() {
    if (!config_.use_pkce) return;
    
    // Generate code verifier (43-128 characters)
    code_verifier_ = generateRandomString(128);
    
    // Generate code challenge (SHA256 hash of verifier, base64url encoded)
    std::string hash = sha256(code_verifier_);
    code_challenge_ = base64UrlEncode(hash);
}

std::string OAuthClient::generateRandomString(size_t length) {
    const std::string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
    std::random_device rd;
    std::mt19937 gen(rd());
    std::uniform_int_distribution<> dis(0, chars.size() - 1);
    
    std::string result;
    result.reserve(length);
    for (size_t i = 0; i < length; ++i) {
        result += chars[dis(gen)];
    }
    return result;
}

std::string OAuthClient::base64UrlEncode(const std::string& input) {
    BIO* bio = BIO_new(BIO_s_mem());
    BIO* b64 = BIO_new(BIO_f_base64());
    BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
    bio = BIO_push(b64, bio);
    
    BIO_write(bio, input.c_str(), input.length());
    BIO_flush(bio);
    
    BUF_MEM* bufferPtr;
    BIO_get_mem_ptr(bio, &bufferPtr);
    
    std::string result(bufferPtr->data, bufferPtr->length);
    BIO_free_all(bio);
    
    // Convert to URL-safe base64
    std::replace(result.begin(), result.end(), '+', '-');
    std::replace(result.begin(), result.end(), '/', '_');
    
    // Remove padding
    result.erase(std::find(result.begin(), result.end(), '='), result.end());
    
    return result;
}

std::string OAuthClient::sha256(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256_CTX sha256;
    SHA256_Init(&sha256);
    SHA256_Update(&sha256, input.c_str(), input.length());
    SHA256_Final(hash, &sha256);
    
    return std::string(reinterpret_cast<char*>(hash), SHA256_DIGEST_LENGTH);
}

bool OAuthClient::initiateAuthorization() {
    try {
        // Start local server for callback
        if (!startLocalServer()) {
            std::cerr << "Failed to start local server for OAuth callback" << std::endl;
            return false;
        }
        
        // Generate PKCE pair if enabled
        generatePKCEPair();
        
        // Generate state parameter for CSRF protection
        state_ = generateRandomString(32);
        
        // Build authorization URL
        std::ostringstream auth_url;
        auth_url << config_.authorization_url;
        auth_url << "?response_type=code";
        auth_url << "&client_id=" << urlEncode(config_.client_id);
        auth_url << "&redirect_uri=" << urlEncode(config_.redirect_uri);
        auth_url << "&scope=" << urlEncode(joinScopes(config_.scopes));
        auth_url << "&state=" << urlEncode(state_);
        
        if (config_.use_pkce) {
            auth_url << "&code_challenge=" << urlEncode(code_challenge_);
            auth_url << "&code_challenge_method=S256";
        }
        
        // Open browser
#ifdef _WIN32
        openUrlWindows(auth_url.str());
#else
        system(("xdg-open '" + auth_url.str() + "'").c_str());
#endif
        
        std::cout << "OAuth authorization initiated. Please complete authentication in your browser." << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Failed to initiate authorization: " << e.what() << std::endl;
        return false;
    }
}

bool OAuthClient::finishAuthorization(int timeout_seconds) {
    auto start_time = std::chrono::steady_clock::now();
    auto timeout = std::chrono::seconds(timeout_seconds);
    
    // Wait for callback with timeout
    while (received_auth_code_.empty() && received_error_.empty()) {
        auto elapsed = std::chrono::steady_clock::now() - start_time;
        if (elapsed > timeout) {
            std::cerr << "Authorization timeout" << std::endl;
            stopLocalServer();
            return false;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
    
    stopLocalServer();
    
    // Check for errors
    if (!received_error_.empty()) {
        std::cerr << "Authorization error: " << received_error_ << std::endl;
        return false;
    }
    
    if (received_auth_code_.empty()) {
        std::cerr << "No authorization code received" << std::endl;
        return false;
    }
    
    // Verify state parameter
    if (received_state_ != state_) {
        std::cerr << "State parameter mismatch - possible CSRF attack" << std::endl;
        return false;
    }
    
    // Exchange code for tokens
    return exchangeCodeForTokens(received_auth_code_);
}

bool OAuthClient::exchangeCodeForTokens(const std::string& auth_code) {
    try {
        // Prepare token request
        std::ostringstream body;
        body << "grant_type=authorization_code";
        body << "&code=" << urlEncode(auth_code);
        body << "&redirect_uri=" << urlEncode(config_.redirect_uri);
        body << "&client_id=" << urlEncode(config_.client_id);
        body << "&client_secret=" << urlEncode(config_.client_secret);
        
        if (config_.use_pkce) {
            body << "&code_verifier=" << urlEncode(code_verifier_);
        }
        
        std::map<std::string, std::string> headers;
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        headers["Accept"] = "application/json";
        
        // Make token request
        std::string response = makeHttpRequest(config_.token_url, "POST", headers, body.str());
        
        if (response.empty()) {
            std::cerr << "Empty response from token endpoint" << std::endl;
            return false;
        }
        
        // Parse JSON response
        Json::Value root;
        Json::Reader reader;
        if (!reader.parse(response, root)) {
            std::cerr << "Failed to parse token response JSON" << std::endl;
            return false;
        }
        
        if (root.isMember("error")) {
            std::cerr << "Token error: " << root["error"].asString() << std::endl;
            return false;
        }
        
        // Extract tokens
        token_data_.access_token = root["access_token"].asString();
        token_data_.refresh_token = root.get("refresh_token", "").asString();
        token_data_.token_type = root.get("token_type", "Bearer").asString();
        
        // Calculate expiration time
        int expires_in = root.get("expires_in", 3600).asInt();
        token_data_.expires_at = std::chrono::system_clock::now() + std::chrono::seconds(expires_in);
        
        // Store tokens securely
        storeTokensSecurely();
        
        std::cout << "OAuth tokens obtained successfully" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Token exchange failed: " << e.what() << std::endl;
        return false;
    }
}

bool OAuthClient::isAuthenticated() {
    if (token_data_.access_token.empty()) {
        return false;
    }
    
    // Check token expiration
    auto now = std::chrono::system_clock::now();
    if (now >= token_data_.expires_at) {
        // Try to refresh token
        return refreshToken();
    }
    
    return true;
}

OAuthClient::AuthStatus OAuthClient::getAuthStatus() {
    AuthStatus status;
    
    if (token_data_.access_token.empty()) {
        status.message = "Not authenticated";
        return status;
    }
    
    status.authenticated = true;
    status.expires_at = token_data_.expires_at;
    
    auto now = std::chrono::system_clock::now();
    auto time_remaining = token_data_.expires_at - now;
    status.expires_in_seconds = std::chrono::duration_cast<std::chrono::seconds>(time_remaining).count();
    status.expires_in_minutes = status.expires_in_seconds / 60;
    
    return status;
}

bool OAuthClient::refreshToken() {
    if (token_data_.refresh_token.empty()) {
        return false;
    }
    
    try {
        // Prepare refresh request
        std::ostringstream body;
        body << "grant_type=refresh_token";
        body << "&refresh_token=" << urlEncode(token_data_.refresh_token);
        body << "&client_id=" << urlEncode(config_.client_id);
        body << "&client_secret=" << urlEncode(config_.client_secret);
        
        std::map<std::string, std::string> headers;
        headers["Content-Type"] = "application/x-www-form-urlencoded";
        headers["Accept"] = "application/json";
        
        // Make refresh request
        std::string response = makeHttpRequest(config_.token_url, "POST", headers, body.str());
        
        if (response.empty()) {
            std::cerr << "Empty response from token refresh" << std::endl;
            logout();
            return false;
        }
        
        // Parse JSON response
        Json::Value root;
        Json::Reader reader;
        if (!reader.parse(response, root)) {
            std::cerr << "Failed to parse refresh response JSON" << std::endl;
            logout();
            return false;
        }
        
        if (root.isMember("error")) {
            std::cerr << "Refresh error: " << root["error"].asString() << std::endl;
            logout();
            return false;
        }
        
        // Update tokens
        token_data_.access_token = root["access_token"].asString();
        if (root.isMember("refresh_token")) {
            token_data_.refresh_token = root["refresh_token"].asString();
        }
        
        // Calculate new expiration time
        int expires_in = root.get("expires_in", 3600).asInt();
        token_data_.expires_at = std::chrono::system_clock::now() + std::chrono::seconds(expires_in);
        
        // Store updated tokens
        storeTokensSecurely();
        
        std::cout << "OAuth tokens refreshed successfully" << std::endl;
        return true;
        
    } catch (const std::exception& e) {
        std::cerr << "Token refresh failed: " << e.what() << std::endl;
        logout();
        return false;
    }
}

std::string OAuthClient::callModel(const std::string& prompt, const std::map<std::string, std::string>& params) {
    if (!isAuthenticated()) {
        throw std::runtime_error("Client not authenticated. Please authenticate first.");
    }
    
    try {
        // Prepare API request
        Json::Value payload;
        payload["prompt"] = prompt;
        payload["max_tokens"] = 50; // Default value
        
        // Add additional parameters
        for (const auto& param : params) {
            if (param.first == "max_tokens") {
                payload["max_tokens"] = std::stoi(param.second);
            } else {
                payload[param.first] = param.second;
            }
        }
        
        Json::StreamWriterBuilder builder;
        std::string json_body = Json::writeString(builder, payload);
        
        std::map<std::string, std::string> headers;
        headers["Content-Type"] = "application/json";
        headers["Accept"] = "application/json";
        headers["Authorization"] = token_data_.token_type + " " + token_data_.access_token;
        
        // Make API request
        std::string api_endpoint = config_.api_base_url + "/completions";
        std::string response = makeHttpRequest(api_endpoint, "POST", headers, json_body);
        
        if (response.empty()) {
            throw std::runtime_error("Empty response from API");
        }
        
        return response;
        
    } catch (const std::exception& e) {
        throw std::runtime_error("Model call failed: " + std::string(e.what()));
    }
}

void OAuthClient::logout() {
    token_data_ = TokenData{};
    deleteStoredTokens();
    std::cout << "OAuth tokens cleared" << std::endl;
}

// Token storage methods (Windows implementation)
#ifdef _WIN32
bool OAuthClient::storeTokensSecurely() {
    try {
        Json::Value token_json;
        token_json["access_token"] = token_data_.access_token;
        token_json["refresh_token"] = token_data_.refresh_token;
        token_json["token_type"] = token_data_.token_type;
        
        auto expires_time_t = std::chrono::system_clock::to_time_t(token_data_.expires_at);
        token_json["expires_at"] = static_cast<int64_t>(expires_time_t);
        
        Json::StreamWriterBuilder builder;
        std::string token_data = Json::writeString(builder, token_json);
        
        std::string target = "quanta_haba_oauth_" + config_.provider_name;
        return storeCredentialWindows(target, token_data);
        
    } catch (const std::exception& e) {
        std::cerr << "Failed to store tokens: " << e.what() << std::endl;
        return false;
    }
}

bool OAuthClient::loadStoredTokens() {
    try {
        std::string target = "quanta_haba_oauth_" + config_.provider_name;
        std::string token_data = retrieveCredentialWindows(target);
        
        if (token_data.empty()) {
            return false;
        }
        
        Json::Value root;
        Json::Reader reader;
        if (!reader.parse(token_data, root)) {
            return false;
        }
        
        token_data_.access_token = root.get("access_token", "").asString();
        token_data_.refresh_token = root.get("refresh_token", "").asString();
        token_data_.token_type = root.get("token_type", "Bearer").asString();
        
        int64_t expires_timestamp = root.get("expires_at", 0).asInt64();
        token_data_.expires_at = std::chrono::system_clock::from_time_t(expires_timestamp);
        
        return !token_data_.access_token.empty();
        
    } catch (const std::exception& e) {
        std::cerr << "Failed to load stored tokens: " << e.what() << std::endl;
        return false;
    }
}

bool OAuthClient::deleteStoredTokens() {
    std::string target = "quanta_haba_oauth_" + config_.provider_name;
    return deleteCredentialWindows(target);
}

bool OAuthClient::storeCredentialWindows(const std::string& target, const std::string& data) {
    CREDENTIAL cred = {};
    cred.Type = CRED_TYPE_GENERIC;
    cred.TargetName = const_cast<LPWSTR>(std::wstring(target.begin(), target.end()).c_str());
    cred.CredentialBlobSize = data.size();
    cred.CredentialBlob = reinterpret_cast<LPBYTE>(const_cast<char*>(data.c_str()));
    cred.Persist = CRED_PERSIST_LOCAL_MACHINE;
    
    return CredWriteW(&cred, 0) != 0;
}

std::string OAuthClient::retrieveCredentialWindows(const std::string& target) {
    PCREDENTIALW pcred;
    std::wstring wtarget(target.begin(), target.end());
    
    if (CredReadW(wtarget.c_str(), CRED_TYPE_GENERIC, 0, &pcred)) {
        std::string result(reinterpret_cast<char*>(pcred->CredentialBlob), pcred->CredentialBlobSize);
        CredFree(pcred);
        return result;
    }
    
    return "";
}

bool OAuthClient::deleteCredentialWindows(const std::string& target) {
    std::wstring wtarget(target.begin(), target.end());
    return CredDeleteW(wtarget.c_str(), CRED_TYPE_GENERIC, 0) != 0;
}

void OAuthClient::openUrlWindows(const std::string& url) {
    ShellExecuteA(NULL, "open", url.c_str(), NULL, NULL, SW_SHOWNORMAL);
}
#endif

// HTTP server implementation
bool OAuthClient::startLocalServer() {
    if (server_running_) {
        return true;
    }
    
    server_running_ = true;
    server_thread_ = std::thread(&OAuthClient::serverLoop, this);
    
    // Give server time to start
    std::this_thread::sleep_for(std::chrono::milliseconds(100));
    
    return true;
}

void OAuthClient::stopLocalServer() {
    if (server_running_) {
        server_running_ = false;
        if (server_thread_.joinable()) {
            server_thread_.join();
        }
    }
}

void OAuthClient::serverLoop() {
#ifdef _WIN32
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
        std::cerr << "WSAStartup failed" << std::endl;
        return;
    }
    
    SOCKET server_socket = socket(AF_INET, SOCK_STREAM, 0);
    if (server_socket == INVALID_SOCKET) {
        std::cerr << "Failed to create socket" << std::endl;
        WSACleanup();
        return;
    }
    
    sockaddr_in server_addr = {};
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = INADDR_ANY;
    server_addr.sin_port = htons(8080);
    
    if (bind(server_socket, reinterpret_cast<sockaddr*>(&server_addr), sizeof(server_addr)) == SOCKET_ERROR) {
        std::cerr << "Failed to bind socket" << std::endl;
        closesocket(server_socket);
        WSACleanup();
        return;
    }
    
    if (listen(server_socket, 1) == SOCKET_ERROR) {
        std::cerr << "Failed to listen on socket" << std::endl;
        closesocket(server_socket);
        WSACleanup();
        return;
    }
    
    while (server_running_) {
        fd_set readfds;
        FD_ZERO(&readfds);
        FD_SET(server_socket, &readfds);
        
        timeval timeout = {1, 0}; // 1 second timeout
        int result = select(0, &readfds, nullptr, nullptr, &timeout);
        
        if (result > 0 && FD_ISSET(server_socket, &readfds)) {
            SOCKET client_socket = accept(server_socket, nullptr, nullptr);
            if (client_socket != INVALID_SOCKET) {
                char buffer[4096];
                int bytes_received = recv(client_socket, buffer, sizeof(buffer) - 1, 0);
                
                if (bytes_received > 0) {
                    buffer[bytes_received] = '\0';
                    std::string request(buffer);
                    
                    // Parse request for authorization code
                    std::regex code_regex(R"(GET /callback\?.*code=([^&\s]+))");
                    std::regex state_regex(R"(GET /callback\?.*state=([^&\s]+))");
                    std::regex error_regex(R"(GET /callback\?.*error=([^&\s]+))");
                    
                    std::smatch match;
                    if (std::regex_search(request, match, code_regex)) {
                        received_auth_code_ = match[1].str();
                    }
                    if (std::regex_search(request, match, state_regex)) {
                        received_state_ = match[1].str();
                    }
                    if (std::regex_search(request, match, error_regex)) {
                        received_error_ = match[1].str();
                    }
                    
                    // Send success response
                    std::string response = "HTTP/1.1 200 OK\r\n"
                                         "Content-Type: text/html\r\n"
                                         "Connection: close\r\n\r\n"
                                         "<!DOCTYPE html><html><head><title>Authentication Successful</title></head>"
                                         "<body><h1>Authentication Successful!</h1>"
                                         "<p>You can close this window and return to the application.</p></body></html>";
                    
                    send(client_socket, response.c_str(), response.length(), 0);
                }
                
                closesocket(client_socket);
                server_running_ = false; // Stop after handling one request
            }
        }
    }
    
    closesocket(server_socket);
    WSACleanup();
#endif
}

// Utility methods
std::string OAuthClient::urlEncode(const std::string& value) {
    std::ostringstream escaped;
    escaped.fill('0');
    escaped << std::hex;
    
    for (char c : value) {
        if (std::isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') {
            escaped << c;
        } else {
            escaped << std::uppercase;
            escaped << '%' << std::setw(2) << int(static_cast<unsigned char>(c));
            escaped << std::nouppercase;
        }
    }
    
    return escaped.str();
}

std::string OAuthClient::joinScopes(const std::vector<std::string>& scopes) {
    std::ostringstream result;
    for (size_t i = 0; i < scopes.size(); ++i) {
        if (i > 0) result << " ";
        result << scopes[i];
    }
    return result.str();
}

std::string OAuthClient::makeHttpRequest(const std::string& url, const std::string& method,
                                       const std::map<std::string, std::string>& headers,
                                       const std::string& body) {
#ifdef _WIN32
    // Windows HTTP implementation using WinHTTP
    // This is a simplified implementation - in production, you'd want more robust error handling
    
    // Parse URL
    std::wstring wurl(url.begin(), url.end());
    
    HINTERNET hSession = WinHttpOpen(L"Quanta Haba OAuth Client/1.0",
                                    WINHTTP_ACCESS_TYPE_DEFAULT_PROXY,
                                    WINHTTP_NO_PROXY_NAME,
                                    WINHTTP_NO_PROXY_BYPASS, 0);
    
    if (!hSession) return "";
    
    URL_COMPONENTS urlComp = {};
    urlComp.dwStructSize = sizeof(urlComp);
    urlComp.dwSchemeLength = -1;
    urlComp.dwHostNameLength = -1;
    urlComp.dwUrlPathLength = -1;
    urlComp.dwExtraInfoLength = -1;
    
    if (!WinHttpCrackUrl(wurl.c_str(), wurl.length(), 0, &urlComp)) {
        WinHttpCloseHandle(hSession);
        return "";
    }
    
    std::wstring hostname(urlComp.lpszHostName, urlComp.dwHostNameLength);
    HINTERNET hConnect = WinHttpConnect(hSession, hostname.c_str(), urlComp.nPort, 0);
    
    if (!hConnect) {
        WinHttpCloseHandle(hSession);
        return "";
    }
    
    std::wstring path(urlComp.lpszUrlPath, urlComp.dwUrlPathLength);
    if (urlComp.lpszExtraInfo) {
        path += std::wstring(urlComp.lpszExtraInfo, urlComp.dwExtraInfoLength);
    }
    
    DWORD flags = (urlComp.nScheme == INTERNET_SCHEME_HTTPS) ? WINHTTP_FLAG_SECURE : 0;
    std::wstring wmethod(method.begin(), method.end());
    
    HINTERNET hRequest = WinHttpOpenRequest(hConnect, wmethod.c_str(), path.c_str(),
                                          NULL, WINHTTP_NO_REFERER,
                                          WINHTTP_DEFAULT_ACCEPT_TYPES, flags);
    
    if (!hRequest) {
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return "";
    }
    
    // Add headers
    for (const auto& header : headers) {
        std::wstring wheader = std::wstring(header.first.begin(), header.first.end()) +
                              L": " + std::wstring(header.second.begin(), header.second.end());
        WinHttpAddRequestHeaders(hRequest, wheader.c_str(), wheader.length(),
                               WINHTTP_ADDREQ_FLAG_ADD);
    }
    
    // Send request
    BOOL result = WinHttpSendRequest(hRequest,
                                   WINHTTP_NO_ADDITIONAL_HEADERS, 0,
                                   const_cast<LPVOID>(static_cast<LPCVOID>(body.c_str())),
                                   body.length(), body.length(), 0);
    
    if (!result) {
        WinHttpCloseHandle(hRequest);
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return "";
    }
    
    result = WinHttpReceiveResponse(hRequest, NULL);
    if (!result) {
        WinHttpCloseHandle(hRequest);
        WinHttpCloseHandle(hConnect);
        WinHttpCloseHandle(hSession);
        return "";
    }
    
    // Read response
    std::string response;
    DWORD bytesAvailable = 0;
    do {
        bytesAvailable = 0;
        if (!WinHttpQueryDataAvailable(hRequest, &bytesAvailable)) break;
        
        if (bytesAvailable > 0) {
            std::vector<char> buffer(bytesAvailable + 1);
            DWORD bytesRead = 0;
            if (WinHttpReadData(hRequest, buffer.data(), bytesAvailable, &bytesRead)) {
                buffer[bytesRead] = '\0';
                response += buffer.data();
            }
        }
    } while (bytesAvailable > 0);
    
    WinHttpCloseHandle(hRequest);
    WinHttpCloseHandle(hConnect);
    WinHttpCloseHandle(hSession);
    
    return response;
#else
    // Linux implementation would use libcurl
    return "";
#endif
}
