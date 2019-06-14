# Stale Conntrack Flusher

## Dockerhub Link
[flush-conntrack](https://cloud.docker.com/repository/docker/suckzoo/flush-conntrack)
[flush-conntrack-trigger](https://cloud.docker.com/repository/docker/suckzoo/flush-conntrack-trigger)


## Overview

(TL;DR) The manifest files in this repository flush stale UDP conntrack.

`hostPort` is a feature that forwards network flow from a host to a container.
When we create a container with `hostPort` and `containerPort`, the host opens port
and forwards every packet flowing into that port to the corresponding port of the container.
We use the `hostPort` feature to let pods communicate with daemonsets, such as datadog agent.

Kubernetes itself supports `hostPort` with its default networking plugin, `kubenet`.
However, not everyone uses kubenet for the sake of convenience of deployment.
Network plugins, like [amazon-vpc-cni-k8s](https://github.com/aws/amazon-vpc-cni-k8s),
fit well with cloud providers like AWS, e.g. the plugin attaches load balancer
whenever an ingress object is created. Most of those plugins are built on top of
[CNI](https://github.com/containernetworking/cni). Especially, the `hostPort` feature
strongly depends on the
[portmap](https://github.com/containernetworking/plugins/tree/master/plugins/meta/portmap)
plugin. 

However, there is a critical bug in the portmap plugin, especially when using UDP protocol.
Whenever pods of the daemonset is broken, the old conntracks are not flushed by portmap.
Thus, the iptables of the portmap points to the old IP address and packets sent to host
are lost as a result. 

This repository provides a workaround. This workaround performs following actions:
1. Trigger a privileged deployment.
2. The privileged deployment flushes every conntrack whose destination IP and port matches.
3. Ta-da


## How to use

1. Create a privileged kubernetes serviceAccount with role and rolebinding, via `kubectl apply -f kubectl.yaml`
2. Create flush-conntrack deployment and services via `kubectl apply -f flush-conntrack.yaml`
3. Add initContainer to your daemonset or anything else, like
```yaml
initContainers:
- name: flush-conntrack-trigger
  image: suckzoo/flush-conntrack-trigger:0.0.1d
  env:
  - name: TARGET_IP
    valueFrom:
      fieldRef:
        fieldPath: status.hostIP
  - name: TARGET_NAMESPACE
    valueFrom:
      fieldRef:
        fieldPath: metadata.namespace
  - name: TARGET_PORT
    value: "8125"
```

## License
MIT

