# sprk

Sprk is a customizable command line tool core, similar in concept to the `argparse` module in the Python standard library. It's intended as a versatile template to be extended and adapted by the user from any directory and to any degree as circumstances and needs change. It does everything by default with a single source file.


- [Getting started](#getting-started)
    - [The basic tool](#the-basic-tool)
    - [Multiple tools](#multiple-tools)
- [Creating a tool](#creating-a-tool)
    - [Runner & Sprker (tool classes)](#runner--sprker-tool-classes)
    - [Task (tool internal class)](#task-tool-internal-class)
- [Providing resources](#providing-resources)
    - [Resource, Process & Option (resource classes)](#resource-process--option-resource-classes)
    - [Pools & ranks](#pools--ranks)
    - [Calls & items](#calls--items)
    - [Host tool use](#host-tool-use)
- [Inserting templates](#inserting-templates)
   - [Template (template class)](#template-template-class)
- [Runtime overview](#runtime-overview)
- [Development plan](#development-plan)

## Getting started

Sprk 1.0.0 is written in Python 3.8.5. On a Linux system with a compatible version of Python installed you should be able to place the sprk source file in the `/usr/bin` directory, make it executable with the below command and call it from any directory with the command `sprk`.

```shell
chmod +x sprk
```

The command `sprk`, `sprk -h` or `sprk --help` will show a help page.

```shell
sprk -h
```

On the help page you'll see that the command `sprk -B` or `sprk --backup` calls a copy of source code to the current directory, as a so-called sprkfile, with the default name 'Sprkfile'. Changes can be made to the code and the changed file copied over the existing sprk source file with the command `sprk -U` or `sprk --update`.

### The basic tool

The source code in this repository provides a simple general command line tool as well as underlying logic for tools of far greater scope and complexity. It offers an example for reference and a starting point for other uses.

It may be best to take a look at the source file and experiment with the options and code before reading further.

### Multiple tools

If you'd like to use more than one version of the source file and avoid a new version's sprkfile being overwritten in error, you can change the value of its `sprkfilename` variable.

It might be more 'sprkic', however, to instantiate an additional tool in the sole source file and append this new tool to the `tools` list. Each tool could then have an option that allows the `tools` list to be displayed, the `active_tool` variable changed and the alternative tool used.

## Creating a tool

A tool can be created by creating an instance of either the `Runner` class or the `Sprker` class.

A configuration dictionary containing certain initial values can be passed when instantiating a tool, as in the source file in this repository.

```python
tool_1 = Sprker({
    "prep": [lambda: print("Starting...")],
    "lead": ["project"],
    "tidy": [lambda: print("Finished.")]
})
```

The values in this case are:

- one lambda to be run before the standard tasks (`prep`) and one after every other stage (`tidy`);
- the name of the 'project' pool as a `lead` pool, those which are given priority over other pools, meaning its tasks will be run before tasks in any pools listed later or not listed (see [Pools & ranks](#pools--ranks)) below.

Other possible keys are `name` for the project name string value, `root`, `code` and `main` for path string values (passed when assigned to `pathlib.Path`) and `batches` for instances of the tool internal Batch class containing items to be built (see [Runtime overview](#runtime-overview) below).

A tool can also be extended by providing resources and inserting templates (see [Providing resources](#providing-resources) and [Inserting templates](#inserting-templates) below).

A new tool should be appended to the `tools` list and one of the tools in this list should be assigned to the `active_tool` variable.

### Runner & Sprker (tool classes)

#### Runner (tool class)

The `Runner` is the basis for the standard tool. It provides for:

- a set of optional actions to be run before the standard tasks (`prep`);
- the running of the standard tasks;
- a composition stage (see [Runtime overview](#runtime-overview) below);
- a build stage for creation of any folders and files;
- a set of final optional actions (`tidy`).

The above order is the order in which these events occur (see [Runtime overview](#runtime-overview) below).

#### Sprker (tool class)

The `Sprker` is a descendant of the `Runner` providing two additional methods, one to back up sprk in the form of a sprkfile and one to update sprk from a sprkfile (see [Getting started](#getting-started) above).

#### Task (tool internal class)

A tool will usually instantiate the `Runner`'s `Task` class once for each flag in the `sprk` command, using the `Option` instance corresponding to the flag and any arguments passed to that flag.

It will also instantiate a task for certain instances of the `Process` resource (see [Resource, Process & Option](#resource-process--option-resource-classes) below).

Once created, tasks are run in the order in which the flags appear in the `sprk` command, subject to the effects of any `pool` and `rank` value (see [Pools & ranks](#pools--ranks) below).

## Providing resources

A resource is an instance of the `Resource` class or one of its descendant `Process` and `Option` classes.

One or more resources can be provided using the `provide_resources` method:

```python
tool_1.provide_resources([resource_1, ...])
```

The order in which the resources are passed is the order in which their info values appear on the help page.

### Resource, Process & Option (resource classes)

#### Resource (resource class)

The `Resource` class has an `info` attribute which takes a string value used on the help page. The variable `{BLANK}` can be passed to create an empty line.

#### Process (resource class)

The `Process` class is a descendant of the `Resource`, also accepting an `info` value.

If the `info` value is not provided, a task is instantiated for this resource every time at least one `Option` instance with the same `pool` string value is used, in an order determined by the respective `rank` integer values (see [Pools & ranks](#pools--ranks) below). This may be useful for auxilliary actions or actions always required for a given pool.

This class also has a `call` attribute - for a function to be run by the given task - and an `items` attribute - for a list of dictionaries defining folders and files to be built by the task (see [Runtime overview](#runtime-overview) below). One of the two values is used by default when the task is run.

#### Option (resource class)

The `Option` class is a descendant of the `Process`, also accepting the `pool`, `rank`, `call` and `items` values, as well as the `char`, `word`, `args` and `desc` string values.

The `char` value is a corresponding single-character flag (e.g. 'a'), the `word` value a multi-character flag (e.g. 'add'), the `args` value any arguments the flag expects, and the `desc` value a description of the task. The four are combined automatically into an `info` value.

#### Sample resource

Below is an example of an `Option` instantiation to enable creation of a project folder, as in the source file in this repository.

```python
Option({
    "pool": "project",
    "rank": 1,
    "desc": "create a project folder here, with NAME if given",
    "word": "folder",
    "char": "f",
    "call": start_project,
    "args": ["[NAME]"]
})
```

The values in this case are:

- a `pool` value of 'project' which ensures that the task is run with other tasks having this value (see [next section](#pools--ranks));
- a `rank` value of 1, ensuring that the task is run before any 'project' pool tasks with a higher integer value (see [next section](#pools--ranks));
- `char`, `word`, `args` and `desc` values giving an `info` value approximating '-f, --folder [NAME]  create a new folder here', meaning the task will be run if the '-f' or '--folder' flag is used;
- a function to be called by the task (`call`).

### Pools & ranks

#### Pools

The `Process` and `Option` classes have a `pool` attribute which can be used to group tasks so that the tasks are run together. To do so, give each `Process` and `Option` instance in the group the same `pool` string value.

If one pool needs to be run before another pool, or before any unpooled tasks, the `pool` string value can be added to the tool's `lead` list, e.g. by including the value in the configuration dictionary when instantiating the tool (see [Creating a tool](#creating-a-tool) above). If the `lead` list contains more than one pool the order of the pools in the list is the order in which the pools are run.

#### Ranks

Instances with a `pool` value can also be given a `rank` integer value to set the order that tasks are run inside their pool. A task created from an instance with a lower integer value will be run before a task from an instance with a higher integer value, e.g. a task with a `rank` value of 1 will run before a task with a `rank` value of 2.

### Calls & items

#### Calls

The `Process` and `Option` classes have a `call` attribute which can take a function to be called when the corresponding task is run. If a resource instance has a `call` attribute, no other action will be taken by its task.

A function given as a `call` value is passed two arguments:

- the resource instance itself as the first parameter;
- any arguments passed to the flag in the `sprk` command as the second parameter (see [Task](#task-tool-internal-class) above).

Passing the resource instance allows resource attributes to be used by the function, e.g. any `items` value, but also gives the function access to the host tool (see [next section](#host-tool-use)).

The number of uses of a particular function can be capped under the `caps` key in the tool's `state` attribute.

New or changed tool state can be returned from the function as a dictionary (see [Host tool use](#host-tool-use) below).

#### Items

Instances can also be given an `items` list of dictionaries defining folders and/or files to be built, with the following possible keys:

- a `dirname` string value to create a folder or a `filename` string value to create a file, in each case with the string as the name (without which a sequentially numbered placeholder is generated);
- in the case of a file, a `content` string value for the file content and/or an `input` dictionary further defining content use;
- in the case of a folder, an optional `items` list containing dictionaries for any nested folders and files;

The `input` dictionary can take a `flag` key with the string value 'w' to write the `content` value over any existing file with the given name, 'a' (the default value) to append the content or 'i' to insert it. In the case of insertion, the `input` dictionary can take the following additional keys:

- an `indent` key with an integer value for number of spaces of indentation (default 4);
- an `anchor` key for the insertion point with a dictionary containing a `string` key with the string value after which to insert, or an `index` key for an integer value (the default, with -1, i.e. the final character) at which to insert;
- a `delims` key with a dictionary containing an `opening` key with the string value (default '\n') to be inserted ahead of the content and/or a `closing` key with the string value (default '') to be inserted after it.

If a resource instance has no `call` attribute but has an `items` attribute, the `items` value is passed to an instance of the tool internal Batch class and queued to be built (see [Runtime overview](#runtime-overview) below).

A `call` function can access any `items` value by use of its first parameter, i.e. the resource instance itself (see [Calls](#calls) above).

#### Sample items

Below is an example of an `items` dictionary for a simple tree with a use of insertion.

```python
{
    "dirname": "folder1",
    "items": [
        {
            "dirname": "folder2"
        },
        {
            "filename": "file1",
            "content": "This is appended content."
        },
        {
            "filename": "file2",
            "content": "this is inserted content",
            "input": {
                "flag": "i",
                "anchor": {
                    "string": "Insert here:"
                },
                "delims": {
                    "opening": "\n-",
                    "closing": ";"
                },
                "indent": 2
            }
        }
    ]
}
```

This creates a directory named 'folder1' containing an empty sub-directory named 'folder2', a file named 'file1' with its content appended and a file named 'file2' with its content inserted. The inserted content is indented by two spaces and positioned following the string 'Insert here:', preceded by a newline and a hyphen and followed by a semi-colon. 

### Host tool use

A tool's `provide_resources` method assigns the tool instance itself to each resource's `tool` attribute. This gives the resource instance access to the tool's attributes and methods.

In addition, when a task is run the resource instance passes itself to any `call` value (see [Calls & items](#calls--items) above), making the tool accessible also to that function.

Most notably, the tool has a `state` attribute which takes a dictionary. This can be supplemented or updated in the form of a dictionary returned by any resource instance's `call` function, allowing values to be stored and used in later tasks.

String values in the source file can be provided with top-level values from tool state dynamically by use of the state variable identifier `{STATE:key}`, where 'key' is the top-level key in the `state` attribute. The entire identifier is replaced with the given value if it exists or a failure message otherwise.

## Inserting templates

The `Template` class can be used in preparing for and performing actions at the composition stage (see [Runtime overview](#runtime-overview) below).

One or more templates can be inserted using the `insert_templates` method:

```python
tool_1.insert_templates([template_1, ...])
```

### Template (template class)

The `Template` class has a `name` attribute which takes a string value for internal reference (without which a sequentially numbered placeholder is generated), a `core` attribute containing by default a list with one item ('parts') and a `form` attribute which takes a dictionary having by default a `parts` key and a `calls` key, each containing an empty list.

The `core`, `parts` and `calls` lists can be extended by values passed at instantiation and provided by tasks at Sprk runtime. The `parts` list, and any other list added to `form`, is intended for values to be processed at the composition stage, while the `calls` list is for functions expected to perform this processing. If a key present in the `form` dictionary is listed in the `core` attribute and that key's list holds at least one item at the composition stage, each function in `calls` is called once with the template instance itself as the sole argument.

### Sample template

Below is an example of a `Template` instantiation, for composition of '-ignore'-type files, e.g. .gitignore, as in the source file in this repository:

```python
Template({
    "name": "ignores",
    "core": ["files"],
    "form": {
        "rein": [],
        "nonr": [],
        "sens": [],
        "files": [],
        "calls": [create_ignores]
    }
})
```

In this case, there are four lists for values provided by tasks at Sprk runtime, three of which identify items to be listed in '-ignore'-type files, specifically:

- `rein` for items which are reinstalled;
- `nonr` for non-runtime items;
- `sens` for sensitive items.

The fourth list, `files`, is for the names of the files to be created. Its key is listed in `core`, meaning that if any filenames are added to the `files` list at runtime, `create_ignores` will be called at the composition stage along with any other functions added to `calls`.

This is a fairly complex example. Take a look at the option instance functions in the source file to see how the tool's `modify_template` method is used to append new values dynamically and how the `create_ignores` function composes the content and queues it for creation at the build stage.

## Runtime overview

1. All tools are instantiated, receive any instances of a resource or template class and are added to the `tools` list, with one assigned to the `active_tool` variable.
2. Any relevant command line arguments are passed to the active tool's `use` method, otherwise the `show_help` method is called.
3. The tool's `do_work` method calls any `prep` functions.
4. At the task execution stage, via the `run_tasks` method, the tool: matches each flag to an option instance, subject to the availability of any `call` function present; queues each option instance and any relevant process instances in instances of the tool internal Task class, each option instance with any relevant arguments; reorders these task instances to prioritize lead pools in lead attribute order and resource instances within pools by rank; for each task instance calls any `call` function present, or otherwise queues in an instance of the tool internal Batch class any `items` list present, to be built at the build stage.
5. At the composition stage, via the `compose_items` method, the tool: queues any template instance where any list referenced by key in its `core` attribute contains one or more items; for each such template calls each function listed in `calls`. 
6. At the build stage, via the `build_batches` method, the tool: for each batch instance and for each dictionary listed in `items` calls any `call` function present; creates any file or folder, descending through any nested items, and generates any names required; in the case of file content, prepares any insertion and replaces identifiers for any variables defined in the tool's `vars` attribute.
7. The tool's `do_work` method calls any `tidy` functions.

## Development plan

The following are possible next steps in the development of the code base. The general medium-term aim is a flexible and fluid toolkit able to support a wide variety of tasks with a low-friction interface. Pull requests are welcome for these and any other potential improvements.

- allow for a confirmation request when overwriting and for precise positioning when appending and inserting content
- add a runtime undo option for rollback on error at the build stage
- offer less verbose or no terminal output at runtime
- support a list of current project directories for ease of movement among them
- include a method for tool switching at runtime
- enable viewing of snippets stored in source file variables
- enable assignment of snippets to source file variables from the command line or a file, possibly by line number or identifier
- enable extraction of configuration, template insertions and resource provisions to extension file for sharing
- add docstring-embedded tests using `doctest` or fuller tests with `unittest`
- reduce method time and space complexity where possible
- revise to more closely conform to PEP 8
- refactor as more Pythonic
