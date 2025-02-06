# Perimeter

<p align="center">
  <img src="images/perimeter.png" alt="Perimeter Logo" width="200" height="200">
</p>

## Table of Contents

- [Description](#description)
- [Getting Started](#getting-started)
  - [Running Perimeter](#running-perimeter)
  - [Configuration](#configuration)
- [Screenshots](#screenshots)
- [Configuring UniFi Network Controller](#configuring-unifi-network-controller)
- [License](#license)

---

## Description

**Perimeter** is a small-scale **RADIUS** server designed to manage connected clients on a local wireless network. It integrates with **UniFi Network Controller**, allowing administrators to authenticate, authorize, and account (AAA) for devices connecting to the network. The project leverages **Docker** for easy deployment and provides a straightforward configuration process.

---

## Getting Started

### Running Perimeter

To quickly start Perimeter using Docker, use the following command:

```sh
docker run -d \
  --name=perimeter \
  -p 1812:1812/udp \
  -p 1813:1813/udp \
  -v $(pwd)/config:/etc/freeradius \
  perimeter:latest
```

#### Explanation of Flags:
- `-d`: Runs the container in detached mode.
- `--name=perimeter`: Assigns the container a specific name.
- `-p 1812:1812/udp`: Maps the RADIUS authentication port.
- `-p 1813:1813/udp`: Maps the RADIUS accounting port.
- `-v $(pwd)/config:/etc/freeradius`: Mounts a custom configuration directory.

Ensure that the **config/** directory contains necessary RADIUS configurations.

---

## Screenshots

Here are some screenshots of **Perimeter** in action:

- **Dashboard View**
  ![Dashboard](images/dashboard.png)
- **Client Authentication Logs**
  ![Logs](images/logs.png)

---

## Configuring UniFi Network Controller

To configure the **UniFi Network Controller** to send **RADIUS authentication and accounting messages** to the **Perimeter** container, follow these steps:

1. **Access the UniFi Controller**
   - Open the UniFi Network Controller web interface.

2. **Navigate to Settings**
   - Go to **Settings** → **Profiles**.

3. **Create a New RADIUS Profile**
   - Click **Create New** → **RADIUS**.
   - Configure the following settings:
     - **Authentication Server:** `<PERIMETER_CONTAINER_IP>`
     - **Authentication Port:** `1812`
     - **Shared Secret:** `<YOUR_SECRET>`
     - **Accounting Server:** `<PERIMETER_CONTAINER_IP>`
     - **Accounting Port:** `1813`
     - **Accounting Shared Secret:** `<YOUR_SECRET>`
     - Enable **Accounting**

4. **Apply Profile to a Wireless Network**
   - Go to **Settings** → **WiFi**
   - Select the desired SSID and **edit**
   - Under **Security**, select **WPA Enterprise**
   - Choose the newly created **RADIUS Profile**
   - Save and apply changes.

5. **Test the Configuration**
   - Connect a device to the network.
   - Check **Perimeter logs** for authentication and accounting messages:

   ```sh
   docker logs -f perimeter
   ```

---

## License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.


