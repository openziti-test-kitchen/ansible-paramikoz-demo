About This Project:
===================

Using This Project:
===================

![Zerto Trust Ansible](diagrams/zero_trust_ansible.png)

ssh-service-zet:
----------------

intercept.v1
```json
{
  "addresses": [
    "ansibletarget1.ziti"
  ],
  "protocols": [
    "tcp"
  ],
  "portRanges": [
    {
      "low": 22,
      "high": 22
    }
  ]
}
```
host.v1
```json
{
  "port": 22,
  "address": "openssh-server",
  "protocol": "tcp"
}
```

ssh-service-sdk:
----------------

intercept.v1
```json
{
  "addresses": [
    "ansibletarget2.ziti"
  ],
  "protocols": [
    "tcp"
  ],
  "portRanges": [
    {
      "low": 22,
      "high": 22
    }
  ]
}
```

```bash
# Copy your newly minted JWT tokens into the expected location
cp ~/Downloads/ssh_{client,server}_?.jwt secrets/tokens/

# Run setup.sh script to:
# 1) Generate needed secrets
# 2) Enroll JWT tokens
# 3) Build service containers
# 4) Start the docker-compose stack
./setup.sh
```
```bash
# List your inventory hosts
ansible "all" --list

# Let's see if we can reach our hosts 
# over the OpenZiti overlay
# provided by ZEDS
ansible "all" -m ping
```

```bash
# Let's prove one of these is not like the other ;)
# ansibletarget1.ziti should fail
# ansibletarget2.ziti should give you a friendly welcome
ansible "all" -m raw -a "ziggywave"
```

```bash
ansible "all" -m setup
```

```bash
# Clean up containers
docker-compose down
```