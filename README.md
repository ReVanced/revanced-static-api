# Static API

Repository to host a static API using GitHub workflows.

## How it works

When CI is ran, static files are generated and commited to the `gh-pages` branch.  
The file `generator.py` provides a list of static file generator classes. Each class has a name.  
The configuration file `config.json` is read which contains the configuration for the API.  
By specifying the name of the generator in the `types` array of the configuration, the corresponding generator will be used. The current object of the configuration is passed to the generator.

The following API configuration generates the `contributor` and `release` API for selected repositories:

```json
{
  "api": [
    {
      "types": ["release", "contributor"],
      "repositories": ["user/repo"]
    }
  ]
}
```

All static files are generated in the output path specified in the configuration.

## Setup

A repository variable `CONFIG` is expected by CD with the configuration (string escaped) which will be used by CD to generate the static files.
