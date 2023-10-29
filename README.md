# Static API

Repository to host a static API using GitHub workflows.

## How it works

When CI is ran, static files are generated and commited to the `gh-pages` branch.  
The file `generator.py` provides a list of static file generator classes. Each class has a name.  
The configuration file `config.json` is read which contains the configuration for the API.  
By specifying the name of the generator in the `generators` array of the configuration, the corresponding generator will be used. The current object of the configuration is passed to the generator.

The following configuration generates static files using the `contributors` and `releases` generator for selected repositories:

```json
{
  "api": [
    {
      "generators": ["releases", "contributors"],
      "repositories": ["user/repo"]
    }
  ]
}
```

All static files are generated in the output path specified in the configuration.  
The `purge` array in the configuration specifies which files should be deleted before generating the static files.

## Setup

A repository variable `CONFIG` is expected by CD with the configuration (string escaped) which will be used by CD to generate the static files.
