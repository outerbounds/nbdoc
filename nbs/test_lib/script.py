"""
This is a module level docstring.
"""

def func(ms) -> str:
    """
    Switch Metadata provider.

    This call has a global effect. Selecting the local metadata will,
    for example, not allow access to information stored in remote
    metadata providers.

    Parameters
    ----------
    ms : string
        Can be a path (selects local metadata), a URL starting with http (selects
        the service metadata) or an explicit specification <metadata_type>@<info>; as an
        example, you can specify local@<path> or service@<url>.

    Returns
    -------
    string
        The description of the metadata selected (equivalent to the result of
        get_metadata())
    """
    global current_metadata
    infos = ms.split("@", 1)
    return get_metadata()


def get_metadata():
    """
    Returns the current Metadata provider.

    This call returns the current Metadata being used to return information
    about Metaflow objects.

    If this is not set explicitly using metadata(), the default value is
    determined through environment variables.

    Returns
    -------
    string
        Information about the Metadata provider currently selected. This information typically
        returns provider specific information (like URL for remote providers or local paths for
        local providers).
    """
    if current_metadata is False:
        default_metadata()
    return True



class Metaflow(object):
    """
    Entry point to all objects in the Metaflow universe.

    This object can be used to list all the flows present either through the explicit property
    or by iterating over this object.

    Attributes
    ----------
    flows : List of all flows.
        Returns the list of all flows. Note that only flows present in the set namespace will
        be returned. A flow is present in a namespace if it has at least one run in the
        namespace.

    """

    def __init__(self):
        # the default namespace is activated lazily at the first object
        # invocation or get_namespace(). The other option of activating
        # the namespace at the import time is problematic, since there
        # may be other modules that alter environment variables etc.
        # which may affect the namescape setting.
        if current_namespace is False:
            default_namespace()
        if current_metadata is False:
            default_metadata()
        self.metadata = current_metadata

    @property
    def flows(self):
        """
        Returns a list of all the flows present.

        Only flows present in the set namespace are returned. A flow is present in a namespace if
        it has at least one run that is in the namespace.

        Returns
        -------
        List[Flow]
            List of all flows present.
        """
        return list(self)

    def __iter__(self):
        """
        Iterator over all flows present.

        Only flows present in the set namespace are returned. A flow is present in a namespace if
        it has at least one run that is in the namespace.

        Yields
        -------
        Flow
            A Flow present in the Metaflow universe.
        """
        # We do not filter on namespace in the request because
        # filtering on namespace on flows means finding at least one
        # run in this namespace. This is_in_namespace() function
        # does this properly in this case
        all_flows = self.metadata.get_object("root", "flow", None, None)
        all_flows = all_flows if all_flows else []
        for flow in all_flows:
            try:
                v = Flow(_object=flow)
                yield v
            except MetaflowNamespaceMismatch:
                continue


class MetaflowObject(object):
    """
    Base class for all Metaflow objects.

    Creates a new object of a specific type (Flow, Run, Step, Task, DataArtifact) given
    a path to it (its `pathspec`).

    Accessing Metaflow objects is done through one of two methods:
      - either by directly instantiating it with this class
      - or by accessing it through its parent (iterating over
        all children or accessing directly using the [] operator)

    With this class, you can:
      - Get a `Flow`; use `Flow('FlowName')`.
      - Get a `Run` of a flow; use `Run('FlowName/RunID')`.
      - Get a `Step` of a run; use `Step('FlowName/RunID/StepName')`.
      - Get a `Task` of a step, use `Task('FlowName/RunID/StepName/TaskID')`
      - Get a `DataArtifact` of a task; use
           `DataArtifact('FlowName/RunID/StepName/TaskID/ArtifactName')`.

    Attributes
    ----------
    tags : Set
        Tags associated with the object.
    created_at : datetime
        Date and time this object was first created.
    parent : MetaflowObject
        Parent of this object. The parent of a `Run` is a `Flow` for example
    pathspec : string
        Pathspec of this object (for example: 'FlowName/RunID' for a `Run`)
    path_components : List[string]
        Components of the pathspec
    origin_pathspec : str
        Pathspec of the original object this object was cloned from (in the case of a resume).
        None if not applicable.
    """

    _NAME = "base"
    _CHILD_CLASS = None
    _PARENT_CLASS = None

    def __init__(
        self,
        pathspec=None,
        attempt=None,
        _object=None,
        _parent=None,
        _namespace_check=True,
    ):
        self._metaflow = Metaflow()
        self._parent = _parent
        self._path_components = None
        self._attempt = attempt

        if self._attempt is not None:
            if self._NAME not in ["task", "artifact"]:
                raise MetaflowNotFound(
                    "Attempts can only be specified for Task or DataArtifact"
                )
            try:
                self._attempt = int(self._attempt)
            except ValueError:
                raise MetaflowNotFound("Attempt can only be an integer")

            if self._attempt < 0:
                raise MetaflowNotFound("Attempt can only be non-negative")
            elif self._attempt >= MAX_ATTEMPTS:
                raise MetaflowNotFound(
                    "Attempt can only be smaller than %d" % MAX_ATTEMPTS
                )
            # NOTE: It is possible that no attempt exists but we can't
            # distinguish between "attempt will happen" and "no such
            # attempt exists".

        if pathspec:
            ids = pathspec.split("/")

            self.id = ids[-1]
            self._pathspec = pathspec
            self._object = self._get_object(*ids)
        else:
            self._object = _object
            self._pathspec = pathspec

        if self._NAME in ("flow", "task"):
            self.id = str(self._object[self._NAME + "_id"])
        elif self._NAME == "run":
            self.id = str(self._object["run_number"])
        elif self._NAME == "step":
            self.id = str(self._object["step_name"])
        elif self._NAME == "artifact":
            self.id = str(self._object["name"])
        else:
            raise MetaflowInternalError(msg="Unknown type: %s" % self._NAME)

        self._created_at = datetime.fromtimestamp(self._object["ts_epoch"] / 1000.0)

        self._tags = frozenset(
            chain(self._object.get("system_tags") or [], self._object.get("tags") or [])
        )

        if _namespace_check and not self.is_in_namespace():
            raise MetaflowNamespaceMismatch(current_namespace)

    def _get_object(self, *path_components):
        result = self._metaflow.metadata.get_object(
            self._NAME, "self", None, self._attempt, *path_components
        )
        if not result:
            raise MetaflowNotFound("%s does not exist" % self)
        return result

    def __iter__(self):
        """
        Iterate over all child objects of this object if any.

        Note that only children present in the current namespace are returned.

        Returns
        -------
        Iterator[MetaflowObject]
            Iterator over all children
        """
        query_filter = {}
        if current_namespace:
            query_filter = {"any_tags": current_namespace}

        unfiltered_children = self._metaflow.metadata.get_object(
            self._NAME,
            _CLASSES[self._CHILD_CLASS]._NAME,
            query_filter,
            self._attempt,
            *self.path_components
        )
        unfiltered_children = unfiltered_children if unfiltered_children else []
        children = filter(
            lambda x: self._iter_filter(x),
            (
                _CLASSES[self._CHILD_CLASS](
                    attempt=self._attempt,
                    _object=obj,
                    _parent=self,
                    _namespace_check=False,
                )
                for obj in unfiltered_children
            ),
        )

        if children:
            return iter(sorted(children, reverse=True, key=lambda x: x.created_at))
        else:
            return iter([])

    def _iter_filter(self, x):
        return True

    def _filtered_children(self, *tags):
        """
        Returns an iterator over all children.

        If tags are specified, only children associated with all specified tags
        are returned.
        """
        for child in self:
            if all(tag in child.tags for tag in tags):
                yield child

    @classmethod
    def _url_token(cls):
        return "%ss" % cls._NAME

    def is_in_namespace(self):
        """
        Returns whether this object is in the current namespace.

        If the current namespace is None, this will always return True.

        Returns
        -------
        bool
            Whether or not the object is in the current namespace
        """
        if self._NAME == "flow":
            return any(True for _ in self)
        else:
            return current_namespace is None or current_namespace in self._tags

    def __str__(self):
        if self._attempt is not None:
            return "%s('%s', attempt=%d)" % (
                self.__class__.__name__,
                self.pathspec,
                self._attempt,
            )
        return "%s('%s')" % (self.__class__.__name__, self.pathspec)

    def __repr__(self):
        return str(self)

    def _get_child(self, id):
        result = []
        for p in self.path_components:
            result.append(p)
        result.append(id)
        return self._metaflow.metadata.get_object(
            _CLASSES[self._CHILD_CLASS]._NAME, "self", None, self._attempt, *result
        )

    def __getitem__(self, id):
        """
        Returns the child object named 'id'.

        Parameters
        ----------
        id : string
            Name of the child object

        Returns
        -------
        MetaflowObject
            Child object

        Raises
        ------
        KeyError
            If the name does not identify a valid child object
        """
        obj = self._get_child(id)
        if obj:
            return _CLASSES[self._CHILD_CLASS](
                attempt=self._attempt, _object=obj, _parent=self
            )
        else:
            raise KeyError(id)

    def __contains__(self, id):
        """
        Tests whether a child named 'id' exists.

        Parameters
        ----------
        id : string
            Name of the child object

        Returns
        -------
        bool
            True if the child exists or False otherwise
        """
        return bool(self._get_child(id))

    @property
    def tags(self):
        """
        Tags associated with this object.

        Tags can be user defined or system defined. This returns all tags associated
        with the object.

        Returns
        -------
        Set[string]
            Tags associated with the object
        """
        return self._tags

    @property
    def created_at(self):
        """
        Creation time for this object.

        This corresponds to the time the object's existence was first created which typically means
        right before any code is run.

        Returns
        -------
        datetime
            Date time of this object's creation.
        """
        return self._created_at

    @property
    def origin_pathspec(self):
        """
        The pathspec of the object from which the current object was cloned.

        Returns:
            str
                pathspec of the origin object from which current object was cloned.
        """
        origin_pathspec = None
        if self._NAME == "run":
            latest_step = next(self.steps())
            if latest_step:
                # If we had a step
                task = latest_step.task
                origin_run_id = [
                    m.value for m in task.metadata if m.name == "origin-run-id"
                ]
                if origin_run_id:
                    origin_pathspec = "%s/%s" % (self.parent.id, origin_run_id[0])
        else:
            parent_pathspec = self.parent.origin_pathspec if self.parent else None
            if parent_pathspec:
                my_id = self.id
                origin_task_id = None
                if self._NAME == "task":
                    origin_task_id = [
                        m.value for m in self.metadata if m.name == "origin-task-id"
                    ]
                    if origin_task_id:
                        my_id = origin_task_id[0]
                    else:
                        my_id = None
                if my_id is not None:
                    origin_pathspec = "%s/%s" % (parent_pathspec, my_id)
        return origin_pathspec

    @property
    def parent(self):
        """
        Returns the parent object of this object or None if none exists.

        Returns
        -------
        MetaflowObject
            The parent of this object
        """
        if self._NAME == "flow":
            return None
        # Compute parent from pathspec and cache it.
        if self._parent is None:
            pathspec = self.pathspec
            parent_pathspec = pathspec[: pathspec.rfind("/")]
            # Only artifacts and tasks have attempts right now so we get the
            # right parent if we are an artifact.
            attempt_to_pass = self._attempt if self._NAME == "artifact" else None
            # We can skip the namespace check because if self._NAME = 'run',
            # the parent object is guaranteed to be in namespace.
            # Otherwise the check is moot for Flow since parent is singular.
            self._parent = _CLASSES[self._PARENT_CLASS](
                parent_pathspec, attempt=attempt_to_pass, _namespace_check=False
            )
        return self._parent

    @property
    def pathspec(self):
        """
        Returns a string representation uniquely identifying this object.

        The string is the same as the one you would pass into the constructor
        to build this object except if you are looking for a specific attempt of
        a task or a data artifact (in which case you need to add `attempt=<attempt>`
        in the constructor).

        Returns
        -------
        string
            Unique representation of this object
        """
        if self._pathspec is None:
            if self.parent is None:
                self._pathspec = self.id
            else:
                parent_pathspec = self.parent.pathspec
                self._pathspec = os.path.join(parent_pathspec, self.id)
        return self._pathspec

    @property
    def path_components(self):
        """
        List of individual components of the pathspec.

        Returns
        -------
        List[string]
            Individual components of the pathspec
        """
        if self._path_components is None:
            ids = self.pathspec.split("/")
            self._path_components = ids
        return list(self._path_components)


class MetaflowData(object):
    def __init__(self, artifacts):
        self._artifacts = dict((art.id, art) for art in artifacts)

    def __getattr__(self, name):
        return self._artifacts[name].data

    def __contains__(self, var):
        return var in self._artifacts

    def __str__(self):
        return "<MetaflowData: %s>" % ", ".join(self._artifacts)

    def __repr__(self):
        return str(self)



class Flow(MetaflowObject):
    """
    A Flow represents all existing flows with a certain name, in other words,
    classes derived from 'FlowSpec'

    As such, it contains all Runs (executions of a flow) related to this flow.

    Attributes
    ----------
    latest_run : Run
        Latest Run (in progress or completed, successfully or not) of this Flow
    latest_successful_run : Run
        Latest successfully completed Run of this Flow
    """

    _NAME = "flow"
    _PARENT_CLASS = None
    _CHILD_CLASS = "run"

    def __init__(self, foo, *args, **kwargs):
        super(Flow, self).__init__(*args, **kwargs)

    @property
    def latest_run(self):
        """
        Returns the latest run (either in progress or completed) of this flow.

        Note that an in-progress run may be returned by this call. Use latest_successful_run
        to get an object representing a completed successful run.

        Returns
        -------
        Run
            Latest run of this flow
        """
        for run in self:
            return run

    @property
    def latest_successful_run(self):
        """
        Returns the latest successful run of this flow.

        Returns
        -------
        Run
            Latest successful run of this flow
        """
        for run in self:
            if run.successful:
                return run

    @property
    def runs(self, *tags):
        """
        Returns an iterator over all the runs in the flow.

        An optional filter is available that allows you to filter on tags.
        If tags are specified, only runs associated with all specified tags
        are returned.

        Parameters
        ----------
        tags : string
            Tags to match

        Returns
        -------
        Iterator[Run]
            Iterator over Run objects in this flow
        """
        self.a = 2
        return self._filtered_children(*tags)


_CLASSES["flow"] = Flow
_CLASSES["run"] = Run
_CLASSES["step"] = Step
_CLASSES["task"] = Task
_CLASSES["artifact"] = DataArtifact
