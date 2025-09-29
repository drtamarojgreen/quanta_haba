#ifndef OAUTH_CLIENT_H
#define OAUTH_CLIENT_H

#include <string>
#include <map>
#include <vector>
#include <memory>
#include <functional>
#include <thread>
#include <atomic>
#include <chrono>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <winhttp.h>
#include <wincred.h>
#include <shellapi.h>
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "winhttp.lib")
#pragma comment(lib, "advapi32.lib")
#pragma comment(lib, "shell32.lib")
#endif

/**
 * OAuth 2.0 Client for External Model Integration (C++)
 * 
 * This class provides a comprehensive OAuth 2.0 implementation for securely
 * authenticating with external language model providers in C++.
 */
class OAuthClient {
public:
    struct OAuthConfig {
        std::string client_id;
        std::string client_secret;
        std::string authorization_url;
        std::string token_url;
        std::string api_base_url;
        std::vector<std::string> scopes;
        std::string redirect_uri = "http://localhost:8080/callback";
        bool use_pkce = true;
        std::string provider_name = "external_model";
    };

    struct AuthStatus {
        bool authenticated = false;
        std::string message;
        std::chrono::system_clock::time_point expires_at;
        int expires_in_seconds = 0;
        int expires_in_minutes = 0;
    };

    struct TokenData {
        std::string access_token;
        std::string refresh_token;
        std::chrono::system_clock::time_point expires_at;
        std::string token_type = "Bearer";
    };

    // Constructor
    explicit OAuthClient(const OAuthConfig& config);
    
    // Destructor
    ~OAuthClient();

    // OAuth flow methods
    bool initiateAuthorization();
    bool finishAuthorization(int timeout_seconds = 300);
    bool isAuthenticated();
    AuthStatus getAuthStatus();
    void logout();

    // API methods
    std::string callModel(const std::string& prompt, const std::map<std::string, std::string>& params = {});

private:
    OAuthConfig config_;
    TokenData token_data_;
    std::string code_verifier_;
    std::string code_challenge_;
    std::string state_;
    
    // HTTP server for callback
    std::atomic<bool> server_running_{false};
    std::thread server_thread_;
    std::string received_auth_code_;
    std::string received_state_;
    std::string received_error_;
    
    // Private methods
    void generatePKCEPair();
    std::string generateRandomString(size_t length);
    std::string base64UrlEncode(const std::string& input);
    std::string sha256(const std::string& input);
    
    bool startLocalServer();
    void stopLocalServer();
    void serverLoop();
    
    bool exchangeCodeForTokens(const std::string& auth_code);
    bool refreshToken();
    
    // Token storage methods
    bool storeTokensSecurely();
    bool loadStoredTokens();
    bool deleteStoredTokens();
    
    // HTTP methods
    std::string makeHttpRequest(const std::string& url, const std::string& method, 
                               const std::map<std::string, std::string>& headers,
                               const std::string& body = "");
    
    // Utility methods
    std::string urlEncode(const std::string& value);
    std::string joinScopes(const std::vector<std::string>& scopes);
    std::map<std::string, std::string> parseQueryString(const std::string& query);
    std::string getCurrentTimestamp();
    
#ifdef _WIN32
    // Windows-specific methods
    bool storeCredentialWindows(const std::string& target, const std::string& data);
    std::string retrieveCredentialWindows(const std::string& target);
    bool deleteCredentialWindows(const std::string& target);
    void openUrlWindows(const std::string& url);
#endif
};

/**
 * Simple HTTP server for handling OAuth callbacks
 */
class SimpleHttpServer {
public:
    SimpleHttpServer(int port = 8080);
    ~SimpleHttpServer();
    
    bool start();
    void stop();
    bool isRunning() const { return running_; }
    
    // Callback data
    std::string getAuthCode() const { return auth_code_; }
    std::string getState() const { return state_; }
    std::string getError() const { return error_; }
    
private:
    int port_;
    std::atomic<bool> running_{false};
    std::thread server_thread_;
    
    std::string auth_code_;
    std::string state_;
    std::string error_;
    
    void serverLoop();
    std::string handleRequest(const std::string& request);
    std::map<std::string, std::string> parseHttpRequest(const std::string& request);
    std::string generateSuccessPage();
    
#ifdef _WIN32
    SOCKET server_socket_;
#endif
};

#endif // OAUTH_CLIENT_H
