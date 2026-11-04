#include <arpa/inet.h>
#include <sys/socket.h>
#include <unistd.h>

#include <cerrno>
#include <charconv>
#include <cstdio>
#include <iostream>
#include <string>
#include <string_view>

bool send_all(int client, std::string_view message) {
    while (!message.empty()) {
        const auto sent = send(client, message.data(), message.size(), MSG_NOSIGNAL);
        if (sent < 0 && errno == EINTR) continue;
        if (sent <= 0) return false;
        message.remove_prefix(sent);
    }
    return true;
}

void echo_lines(int client) {
    constexpr std::size_t max_line = 4096; // Excludes the newline.
    char chunk[1024];
    std::string pending;
    for (;;) {
        const auto count = recv(client, chunk, sizeof(chunk), 0);
        if (count < 0 && errno == EINTR) continue;
        if (count <= 0) return;
        for (char byte : std::string_view(chunk, count)) {
            if (byte != '\n' && pending.size() == max_line) return;
            pending.push_back(byte);
            if (byte == '\n') {
                if (!send_all(client, pending)) return;
                pending.clear();
            }
        }
    }
}

int main(int argc, char** argv) {
    unsigned int port = 9000;
    if (argc == 2) {
        const std::string_view input(argv[1]);
        const auto end = input.data() + input.size();
        const auto result = std::from_chars(input.data(), end, port);
        if (result.ec != std::errc{} || result.ptr != end || port > 65535) {
            std::cerr << "Port must be between 0 and 65535\n";
            return 1;
        }
    } else if (argc != 1) {
        std::cerr << "Usage: tcp_echo [port]\n";
        return 1;
    }

    const int listener = socket(AF_INET, SOCK_STREAM, 0);
    if (listener < 0) {
        std::perror("socket");
        return 1;
    }

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    address.sin_port = htons(port);
    socklen_t address_size = sizeof(address);
    if (bind(listener, reinterpret_cast<sockaddr*>(&address), address_size) < 0 ||
        listen(listener, SOMAXCONN) < 0 ||
        getsockname(listener, reinterpret_cast<sockaddr*>(&address), &address_size) < 0) {
        std::perror("listen setup");
        close(listener);
        return 1;
    }
    std::cout << ntohs(address.sin_port) << std::endl;

    for (;;) {
        const int client = accept(listener, nullptr, nullptr);
        if (client < 0 && errno == EINTR) continue;
        if (client < 0) {
            std::perror("accept");
            close(listener);
            return 1;
        }
        echo_lines(client);
        close(client);
    }
}
