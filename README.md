
# LetsEncrypt Autodeploy

This little program can be used to automate the deployment of different certificates from a centralized certification server based on a very simple json based rule set.




## Useage

Copy this repository to your certificate Server or deployment point and paste the script with symlink in "/etc/letsencrypt/renewal-hooks/deploy/". Example command: ln -s /opt/auto_deploy.py /etc/letsencrypt/renewal-hooks/deploy/auto_deploy.py 

Create a config like given in the example and create your signing request.

Only Python3 is required. This Script is used as "deploy-hook" Script. In the following is an example Script used by me.


```
sudo certbot certonly \ 
    --authenticator <<your auth plugin>> \
    --dns-netcup-credentials /path/to/your/plugin/credentials \ 
    --dns-netcup-propagation-seconds 900 \
    --keep-until-expiring \
    --non-interactive \
    --expand \
    --server https://acme-v02.api.letsencrypt.org/directory \ 
    --agree-tos \
    --email your@mail.com \
    -d 'domain.tld' \
    -d '*.domain.tls' 
```
    
## Configuration

Per default the config path is "./config.json" if you want to change this you can use the "-config" Parameter.

In the following is an example Configuration for two example domains

```json
{
    "domain.tld": 
    [
        {
            "wildcard": true,
            "base": true,
            "domains": [
              "*"
            ],
            "target": [
              "/path/to/your/targetdir1",
              "/path/to/your/targetdir2"
            ]
        },
        {
            "wildcard": false,
            "base": false,
            "domains": [
              "mail", "www", "service"
            ],
            "target": [
              "/path/to/your/targetdir1",
              "/path/to/your/targetdir2"
            ]
        }
    ],
    "domain2.tld": 
    [
        {
            "wildcard": true,
            "base": true,
            "domains": [
              "*"
            ],
            "target": [
              "/path/to/your/targetdir1",
              "/path/to/your/targetdir2"
            ]
        }
    ]
}
```

*wildcard* => The wildcard key is used to cover wildcard certificates (*.domain.tld).
*base* => The base key is used to cover the bare domain certificate (domain.tld)
*domains* => In this array you can define all subdomains you want to cover (only one subdomain is currently supported if you need more open an issue and I will ad this feature if needed. - sub.domain.tld => Supported, 2nd.sub.domain.tld => Not working!)




