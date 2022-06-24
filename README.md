# Zero Trust Ansible Demo

But...why?

Seeing is believing, but feeling is the truth. Sometimes, you must touch it to get a sense of the thing.

More practically, because Ansible is widely deployed and probably used within your organization. Most deployments (not yours, of course) are insecure. More often than not, we defend our precious SSHD servers by limiting their use to the walled garden of the firewall, where the server can listen on its port happily, though perhaps naively. Sadly, sometimes we see this scenario when the host is exposed to the WAN, often relying solely on the security of cryptography to protect them. To make matters worse, many deployments leverage a service user with shared credentials per environment. Sometimes, they invoke Ansible from a centralized server, and sometimes that user has password-less sudo.

 High-performing organizations can do better by forcing administrators to act in the context of their organizational user, with appropriate credentials. But even this approach is limited to the trust domain of the network. Managing things at the edge still poses a challenge, and SSH is often a non-starter for managing globally distributed and vendored services, where SSH connection cannot be reliably established, if at all.

Enter ParamikoZ, Python SSH with built-in OpenZiti!

"If we cannot pass over the mountain, let us go under it" - Gimli son of Gloin

## The Bird's Eye View

So, we are basically going to make this:

![Zerto Trust Ansible](diagrams/zero_trust_ansible.png)

What is this you ask?

1) An Ansible client
2) A couple of  Ziti Edge Developer Sandbox (ZEDS) apps
3) A docker-compose stack of a couple of SSH server services

That means, we need...

### Requirements

1. Python
1. OpenZiti Python SDK
1. Docker Engine (or Podman Socket)
    * Player'ss choice on rootful vs rootless, both work
1. docker-compose (or podman-compose integration)
1. Ansible CLI

There is a `requirements.txt` file at the root of the project. It will install `ansible` and the `openziti` PyPI module.

```bash
# You can use virtualenv or venv, player's choice
pip install --user -r requirements.txt
```

**Whoah, whoah there buddy...that's a lot stuff. "Zero Trust" you say, well why don't we talk about what are we doing here for a second?**

## Our Objective

Before going any further, be aware this explainer is accompanied by a `setup.sh` script and video that will step through doing all. Still, it's important to get some footing before jumping off the deep end.

We are going to deploy some non-privileged SSH servers locally, sandboxed away in containers. One of them, will be behind our `ziti-edge-tunnel` software container in a shared network. The other is a custom, paramiko based ssh server that has been "zitified" with our brand new `python-sdk-py`. Importantly, these containers **don't listen on any public interface, don't have any special Capabilities, and have NO ports mapped to them**. You yourself should not be able to reach them at any port from your host.

With OpenZiti, *we'll still be able to reach them*.

But, only after setting up an OpenZiti Overlay Network. For that, we're going to use the Ziti Enterprise Developer Sandbox (ZEDS). It allows us to set up OpenZiti networks for development purposes, without having to worry about all the underlying ziti components (like the ziti-controller, ziti-router(s), policies, etc...). Don't worry, we're gonna show you how, and give you everything you need below via a short video and some configs you can copy and paste.

Finally, we want to do some work with Ansible. That's were our ParamikoZ connection plugin comes in. Right now, it's less that 60 LOC; yet, it's fully integrated to Ansible's configuration hooks, and allows you to connect (using a ziti identity) to your services. Using this plugin, we supercharge Ansible, by conferring it he powers to find the ZEDS defined service intercept addresses, which are only reachable via the OpenZiti overlay, and which will be hosted on those dark containers. Lastly, we have some eastereggs, so stick around.

## Into the Wild

Let's get familiar with ZEDS.

The video below steps through the UI to show you how this is done. **It is important that you follow the naming conventions shown in the video verbatim, as we will rely on them in the `setup.sh` script**

We're going to create two ZEDS "apps". For our pursposes here, you can think of "apps" as independent OpenZiti overlay networks. ZEDS does the heavy lifting for you, taking away the need to set up your own network.

For each of these apps, we will provision a client identity and a server identity, each one being a JWT token. The client identity will be used for the Ansible paramikoz plugin, and the server identity will be used for the ziti component of the ssh server running in the container.

Then we will create a service definition for each app. These service definitions provide the Ansible hostnames, via a config type called `intercept.v1`, which provides a hostname resolution mechanism for the ParamikoZ plugin.

The `ssh-service-zet` (**z**iti-**e**dge-**t**unnel) will also have a `host.v1` configuration, which the tunnel will use to off-board data from the overlay network. The `ssh-service-sdk` does not need this because the overlay terminates **directly** in the code.

As you step through the video, feel free to use the copy bottons below on the json configs to save you from typing, and to ensure a consistent experience.

[video]

### `ssh-service-zet`

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

### `ssh-service-sdk`

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

## Showtime

If you've followed the steps in the videos, you should now have 4 JWT tokens in your downloads folder.

* ssh_client_{1,2}.jwt
* ssh_server_{1,2}.jwt

You should also have copied the fully qualified service name of the `ssh-service-sdk` service into your clipboard.

Before running the `setup.sh`, please follow these steps:

```bash
# Copy your newly minted JWT tokens into the expected location
cp ~/Downloads/ssh_{client,server}_?.jwt secrets/tokens/
```

```bash
# Export your SDK app service name
export ZITI_SDK_SERVICE="[my_app_name] ssh-service-sdk [my_base64_string]"
```

```bash
# Run setup.sh script to:
# 1) Generate needed secrets
# 2) Enroll JWT tokens
# 3) Build service containers
# 4) Start the docker-compose stack
./setup.sh
```

### The Payoff

You've made it here. Congratulations! Welcome to Zero Trust Ansible. Step forward and claim your prize.

```bash
# List your inventory hosts
ansible "all" --list

# Let's see if we can reach our hosts 
# over the OpenZiti overlay
# provided by ZEDS
ansible "all" -m ping
```

**This should look indestinguishable from any other ansible run**. So, what's going on here?

```bash
ansible "all" --extra-vars 'ziti_log_level=3' -m ping
```

You should now see a bunch of debug information written to stdout by the `ziti-python-sdk`.

Let's try something more taxing. Does this work for you?

```bash
ansible "all" -m setup
```

So, what's going on here?

### The Prestige

Each time a connection is made to the defined `intercept.v1` addresses, the `ParamikoZ` connection plugin rewrites the request at runtime, and sends it on it's way over the overlay. You are accessing your remote SSH servers **over** OpenZiti. Remember, there are *no ports* open on the containers; they are sandboxed away and you can't reach them yourself over your local network.

 The ziti components in those containers are establishing duplexed connections outbound to the ziti network.  

If you provide your own server using one of our SDKs, you can also do some more fun things:

```bash
# Let's prove one of these is not like the other ;)
# ansibletarget1.ziti should fail
# ansibletarget2.ziti should give you a friendly welcome
ansible "all" -m raw -a "ziggywave"
```

### The End

All good things do come to an end. When you're ready, just run:

```bash
# Clean up containers
docker-compose down
```
