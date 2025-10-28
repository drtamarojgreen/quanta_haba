#ifndef OAUTH_CLIENT_H
#define OAUTH_CLIENT_H

#include <string>
#include <vector>
#include <map>
#include <chrono>
#include <thread>

#ifdef _WIN32
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")
#pragma comment(lib, "crypt32.lib")
#pragma comment(lib, "winhttp.lib")
#else
//
#endif

struct OAuthConfig {
    std::string provider_name;
    std::string client_id;
    std::string client_secret;
    std::string authorization_url;
    std::string token_url;
    std::string api_base_url;
    std::string redirect_uri;
    std::vector<std::string> scopes;
    bool use_pkce;
};

class OAuthClient {
public:
    struct TokenData {
        std::string access_token;
        std::string refresh_token;
        std::string token_type;
        std::chrono::system_clock::time_point expires_at;
    };

    struct AuthStatus {
        bool authenticated = false;
        std::chrono::system_clock::time_point expires_at;
        long long expires_in_seconds = 0;
        long long expires_in_minutes = 0;
        std::string message;
    };

    OAuthClient(const OAuthConfig& config);
    ~OAuthClient();

    bool initiateAuthorization();
    bool finishAuthorization(int timeout_seconds = 120);
    bool isAuthenticated();
    AuthStatus getAuthStatus();
    bool refreshToken();
    std::string callModel(const std::string& prompt, const std::map<std::string, std::string>& params = {});
    void logout();

private:
    OAuthConfig config_;
    TokenData token_data_;
    std::string code_verifier_;
    std::string code_challenge_;
    std::string state_;

    // For local server
    std::thread server_thread_;
    bool server_running_ = false;
    std::string received_auth_code_;
    std::string received_state_;
    std::string received_error_;

    void generatePKCEPair();
    bool startLocalServer();
    void stopLocalServer();
    void serverLoop();

    bool exchangeCodeForTokens(const std::string& auth_code);
    bool storeTokensSecurely();
    bool loadStoredTokens();
    bool deleteStoredTokens();
    
    // Platform-specific helpers
#ifdef _WIN32
    bool storeCredentialWindows(const std::string& target, const std::string& data);
    std::string retrieveCredentialWindows(const std::string& target);
    bool deleteCredentialWindows(const std::string& target);
    void openUrlWindows(const std::string& url);
#endif

    // Utility methods
    static std::string generateRandomString(size_t length);
    static std::string base64UrlEncode(const std::string& input);
    static std::string sha256(const std::string& input);
    static std::string urlEncode(const std::string& value);
    static std::string joinScopes(const std::vector<std::string>& scopes);
    static std::string makeHttpRequest(const std::string& url, const std::string& method,
                                     const std::map<std::string, std::string>& headers,
                                     const std::string& body);
};

#endif // OAUTH_CLIENT_H
