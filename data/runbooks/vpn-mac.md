# VPN Setup on macOS

Applies to: company laptops running macOS 12 or newer.

1. Open System Settings > VPN > Add VPN Configuration > IKEv2.
2. Set the display name to "CorpVPN" and the server address to vpn.example-corp.com.
3. Set the remote ID to vpn.example-corp.com.
4. Choose "Username" as authentication and enter your company username.
5. Click Create, then switch "CorpVPN" on.
6. Approve the second-factor prompt on your phone.

If macOS shows "Connection failed", remove the profile and add it again.