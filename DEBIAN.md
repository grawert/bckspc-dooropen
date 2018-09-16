# Build Debian package


## Install software requirements

```shell
sudo apt-get install build-essential quilt make dh-make
```

## Create original source package

```shell
dh_make --createorig
```

## Create Debian package

```shell
dpkg-buildpackage -us -uc -ui -i
```
