"""TODO"""
# pylint: disable=pointless-statement,expression-not-assigned

from diagrams import Cluster, Diagram, Edge
from diagrams.custom import Custom
from diagrams.onprem.container import Docker
from diagrams.onprem.iac import Ansible

graph_attr = {
    "fontname": "Open Sans",
    "fontsize": "32",
}

cluster_attr = {
    "fontname": "Open Sans Semibold",
    "fontsize": "16"
}

with Diagram("Zero Trust Ansible", graph_attr=graph_attr):
    with Cluster("ssh_client_{1,2}", graph_attr=cluster_attr):
        ansible_client = Ansible("ParamikoZ")
    zeds = Custom(
        "", "./assets/ZEDS.png",
        height="4", width="6", imagescale="false"
    )

    with Cluster(""):
        docker = Docker()

        with Cluster("ssh_server_1", graph_attr=cluster_attr):
            zet = Custom("Ziti Edge Tunnel", "./assets/Ziti-Tunnler-App.png")
            sshd = Custom("OpenSSH", "./assets/OpenSSHLogo.png")

        with Cluster("ssh_server_2", graph_attr=cluster_attr):
            sdk = Custom("ParamikoZ SSHD", "./assets/ziti-sdk-py.png")

    ansible_client >> zeds
    zeds << sdk
    zeds << zet
    zet >> sshd
    sdk - Edge(style="invis") - docker
