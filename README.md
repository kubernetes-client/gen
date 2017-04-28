# This repo is for testing new client library structure

# gen
Common generator scripts for all client libraries

# Badges

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Bronze-blue.svg?style=plastic&colorB=cd7f32&colorA=306CE8)](https://github.com/kubernetes-client)

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Silver-blue.svg?style=plastic&colorB=C0C0C0&colorA=306CE8)](https://github.com/kubernetes-client)

[![Client Support Level](https://img.shields.io/badge/Kubernetes%20client-Gold-blue.svg?style=plastic&colorB=FFD700&colorA=306CE8)](https://github.com/kubernetes-client)

#Generating a client
To generate a client, first make sure the client generator exists. For any language other than
go, check `openapi/` folder for a script with `${CLIENT_LANGUAGE}.sh` and run this command:

```bash
${CLIENT_LANGUAGE}.sh OUTPUT_DIR SETTING_FILE
```

`SETTING_FILE` is a bash script exporting required setting to generate a client. These
are normally:

- `KUBERNETES_BRANCH`: The kubernetes branch to get OpenAPI spec from.
- `CLIENT_VERSION`: Client version string. e.g. 1.0.0b1
- `PACKAGE_NAME`: Package name for the generated client. e.g. "kubernetes"

Settings may differ from language to language. Refer to language script's help page for
more information.

