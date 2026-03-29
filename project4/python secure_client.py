A. Client-Side Pseudocode

FUNCTION SecureClientConnect(server_address, server_port):

    tcp_socket = CreateTCPConnection(server_address, server_port)

    tls_context = CreateTLSContext(protocol_version="TLS_1.3")
    tls_socket = tls_context.WrapSocket(tcp_socket)

    certificate = tls_socket.GetServerCertificate()

    IF NOT VerifyCertificate(certificate, trusted_CAs):
        TerminateConnection("Security Alert: Invalid Certificate (Possible MITM)")
        RETURN Error

    tls_socket.CompleteHandshake()

    encrypted_data = "Sensitive Data"
    tls_socket.Send(encrypted_data)

    response = tls_socket.Receive()
    HandleResponse(response)

END FUNCTION


B. Server-Side Pseudocode

FUNCTION SecureServerListen(port):

    tls_context = CreateTLSContext(protocol_version="TLS_1.3")
    tls_context.LoadCertificate("server_cert.pem", "private_key.pem")

    server_socket = BindAndListen(port)

    LOOP FOREVER:
        client_socket = server_socket.Accept()

        TRY:
            tls_conn = tls_context.WrapSocket(client_socket)
            tls_conn.PerformHandshake()

            request = tls_conn.Receive()
            result = ProcessSecurely(request)

            tls_conn.Send(result)

        CATCH TLS_Error:
            Log("Handshake Failed: Possible MITM Attack")

        FINALLY:
            tls_conn.Close()

    END LOOP

END FUNCTION


3. TLS Handshake Process Explanation

Step 1: ClientHello
The client initiates communication by sending supported TLS versions, cipher suites, and a random number.

Step 2: ServerHello and Certificate
The server responds with selected cipher suite, its random number, and a digital certificate issued by a trusted Certificate Authority (CA).

Step 3: Certificate Validation
The client verifies:
- Certificate is signed by trusted CA
- Certificate is not expired
- Domain matches server

Step 4: Key Exchange
Client and server securely exchange keys (e.g., ECDHE) to generate a shared session key.

Step 5: Secure Communication
All communication is encrypted using the session key, ensuring confidentiality and integrity.