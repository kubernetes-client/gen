# gen
Common generator scripts for all client libraries

# Badges

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Bronze-blue.svg?style=plastic&colorB=cd7f32&colorA=306CE8)](https://github.com/kubernetes-client)

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Silver-blue.svg?style=plastic&colorB=C0C0C0&colorA=306CE8)](https://github.com/kubernetes-client)

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Gold-blue.svg?style=plastic&colorB=FFD700&colorA=306CE8)](https://github.com/kubernetes-client)

# Generating a client

To generate a client, first make sure the client script supports the language.
Check the `openapi/` folder and run this command:

```bash
client.sh OUTPUT_DIR SETTING_FILE LANGUAGE
```

`OUTPUT_DIR` is where to put the generated client files.

`SETTING_FILE` is a bash script exporting required setting to generate a client. These
are normally:

- `KUBERNETES_BRANCH`: The kubernetes branch to get OpenAPI spec from. e.g. "master"
- `CLIENT_VERSION`: Client version string. e.g. "1.0.0b1"
- `PACKAGE_NAME`: Package name for the generated client. e.g. "kubernetes"

Example settings file for python-client:

export KUBERNETES_BRANCH="master"
export CLIENT_VERSION="8.0.0b1"
export PACKAGE_NAME="client"

Note: For generating the client for any language, the PACKAGE_NAME should be "client".
      You can use the latest version for the CLIENT_VERSION. It's displayed here for
      the python-client (https://github.com/kubernetes-client/python), and similarly
      for other language clients.

`LANGUAGE` is one of the available client languages, which are currently:

- c
- csharp
- go
- haskell
- java
- perl
- python
- ruby
- typescript

The recommended structure is to generate the client in a folder called
`kubernetes` at the root of the client repo and put all settings in a file named
`settings` at the root of the repo. If you followed these recommendations, you
can simply run autoupdate script anywhere inside the client repo:

```bash
cd ${CLIENT_ROOT}/...
${GEN_REPO_ROOT}/openapi/autoupdate.sh
```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to contribute.
