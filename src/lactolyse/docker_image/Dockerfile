FROM docker.io/fedora:27

LABEL MAINTAINER Domen Blenkuš <domen@blenkus.com>

RUN rpmkeys --import file:///etc/pki/rpm-gpg/RPM-GPG-KEY-fedora-27-x86_64 && \
    dnf install -y --setopt=tsflags=nodocs \
      texlive-scheme-basic  \
      texlive-collection-pictures \
      texlive-collection-xetex \
      texlive-makecell && \
    dnf clean all

CMD ["/bin/bash"]
