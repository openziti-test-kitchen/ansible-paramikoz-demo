Zero Trust Ansible Demo:
===================
But...why? 

Seeing is believing, but feeling is the truth. Sometimes, you have to touch it to get a sense of the thing.

More practically, because Ansible is widely deployed, and probably used within your organization. Most deployments (not yours of course) are insecure. More often than not, we defend our precious SSHD servers by limiting their use to the walled garden of the firewall, where the server can listen on its port happily, though perhaps neively. Sadly, sometimes we see this scenario when the host is exposed to the WAN, often relying solely on the security of cryptography to protect them. To make matters worse, many deployments leverage a service user, with shared credentials per environment. Sometimes, they invoke Ansible from a centralized server, sometimes that user has passwordless sudo.

 High performing organizations can do better by forcing administrators to act in the context of their own organizational user, with appropriate credentials. But even this approach is limited to the trust domain of the network. Managing things at the Edge still poses a challeng, and SSH is often a non-starter for managing globally distributed and vendored services, where SSH connection cannot be reliably established, if at all.

Enter OpenZit and ParamikoZ. 

"If we cannot pass over the mountain, let us go under it" - Gimli son of Gloin

The bird's eye view:
==========================

So, we are basically going to make this:

![Zerto Trust Ansible](diagrams/zero_trust_ansible.png)

What is this you ask?

1) An Ansible client
2) A couple of  Ziti Edge Developer Sandbox (ZEDS) apps
3) A docker-compose stack of a couple of SSH server services

That means, we need...

Requirements:
-------------
1) Python 
2) OpenZiti Python SDK
2) Docker Engine (or Podman Socket)
   * Player'ss choice on rootful vs rootless, both work
3) docker-compose (or podman-compose integration)
4) Ansible CLI

There is a `requirements.txt` file at the root of the project. It will install `ansible` and the `openziti` PyPI module.

```bash
# You can use virtualenv or venv, player's choice
pip install --user -r requirements.txt
```
**Whoah, whoah there buddy...that's a lot stuff. "Zero Trust" you say, well why don't we talk about what are we doing here for a second?**

Objective:
----------
Before going any further, be aware this explainer is accompanied by a `setup.sh` script and video that will step through doing all. Still, it's important to get some footing before jumping off the deep end.

We are going to deploy some non-privileged SSH servers locally, sandboxed away in containers. One of them, will be behind our `ziti-edge-tunnel` software container in a shared network. The other is a custom, paramiko based ssh server that has been "zitified" with our brand new `python-sdk-py`. Importantly, these containers **don't listen on any public interface, don't have any special Capabilities, and have NO ports mapped to them**. You yourself should not be able to reach them at any port from your host. 

With OpenZiti, *we'll still be able to reach them*.

But, only after setting up an OpenZiti Overlay Network. For that, we're going to use the Ziti Enterprise Developer Sandbox (ZEDS). It allows us to set up OpenZiti networks for development purposes, without having to worry about all the underlying ziti components (like the ziti-controller, ziti-router(s), policies, etc...). Don't worry, we're gonna show you how, and give you everything you need below via a short videa and some configs you can copy and paste.

Finally, we want to do some work with Ansible. That's were our ParamikoZ connection plugin comes in. Right now, it's less that 60 LOC; yet, it's fully integrated to Ansible's configuration hooks, and allows you to connect (using a ziti identity) to your services. Using this plugin, we supercharge Ansible, by confering it he powers to find the ZEDS defined service intercept addresses, which are only reachable via the OpenZiti overaly, and which will be hosted on those dark containers. Lastly, we have some eastereggs, so stick around. 

Into the Wild:
============


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
```
```bash
# Export your SDK app service name
export ZITI_SDK_SERVICE="[my_app_name] [my_service_name] [my_base64_string]
```
```bash
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