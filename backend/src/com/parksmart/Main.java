package com.parksmart;

import com.parksmart.handler.ApiHandler;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import com.sun.net.httpserver.HttpServer;

import java.io.*;
import java.net.InetSocketAddress;
import java.nio.file.*;
import java.util.concurrent.Executors;

/**
 * Entry point – starts an HTTP server on port 8080.
 *
 *  /api/*  → ApiHandler   (JSON REST API + JDBC → MySQL)
 *  /*      → StaticHandler (serves frontend/ files)
 *
 * Open http://localhost:8080 in your browser after running run.bat
 */
public class Main {

    static final int    PORT         = 8080;
    static final String FRONTEND_DIR = resolveFrontendDir();

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(PORT), 0);
        server.createContext("/api/",  new ApiHandler());
        server.createContext("/",      new StaticHandler());
        server.setExecutor(Executors.newFixedThreadPool(4));
        server.start();

        System.out.println("==============================================");
        System.out.println("  ParkSmart is running!");
        System.out.println("  URL  : http://localhost:" + PORT);
        System.out.println("  DB   : jdbc:mysql://localhost:3306/parksmart");
        System.out.println("  Stop : Ctrl + C");
        System.out.println("==============================================");
    }

    private static String resolveFrontendDir() {
        // When run.bat executes from backend/, user.dir = .../ParkSmart/backend
        // Frontend lives at .../ParkSmart/frontend
        return Paths.get(System.getProperty("user.dir"), "..", "frontend")
                    .toAbsolutePath().normalize().toString();
    }

    // ── Static file server ──────────────────────────────────────────────────

    static class StaticHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange ex) throws IOException {
            String uriPath = ex.getRequestURI().getPath();
            if (uriPath.equals("/") || uriPath.isEmpty()) uriPath = "/index.html";

            Path file = Paths.get(FRONTEND_DIR, uriPath.substring(1)).normalize();

            // Safety: don't allow path traversal outside frontend/
            if (!file.startsWith(FRONTEND_DIR) || !Files.exists(file) || Files.isDirectory(file)) {
                file = Paths.get(FRONTEND_DIR, "index.html");
            }

            byte[] data = Files.readAllBytes(file);
            ex.getResponseHeaders().set("Content-Type", mime(file.toString()));
            ex.sendResponseHeaders(200, data.length);
            try (OutputStream os = ex.getResponseBody()) { os.write(data); }
        }

        private String mime(String path) {
            if (path.endsWith(".html")) return "text/html; charset=utf-8";
            if (path.endsWith(".css"))  return "text/css; charset=utf-8";
            if (path.endsWith(".js"))   return "application/javascript; charset=utf-8";
            if (path.endsWith(".png"))  return "image/png";
            if (path.endsWith(".ico"))  return "image/x-icon";
            return "application/octet-stream";
        }
    }
}
