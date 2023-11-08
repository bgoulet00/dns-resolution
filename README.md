# dns-resolution
compare source list of hostnames/IPs to DNS entries for those hostnames

This script will import a reference hostname/IP source and then compare that information to active DNS records.
As written, DNS queries will be sent to the DNS servers programmed on the system the script is being run.
With some modification the DNS queries could be directed to any arbitrary DNS system.
The script was designed to be extensible, making it trivial to add options/functions to import hostname/IP from additional sources
beyond csv or solarwinds 


 Developed and tested with the following environment
 - OS: windows
 - Python: 3.11.5
 - Target platform:  Solarwinds Orion 2023.1.1
 - Dependencies: solarwinds capability requires install of orionsdk
