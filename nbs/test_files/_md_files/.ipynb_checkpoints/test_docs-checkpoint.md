<DocSection type="function" name="function_with_types_in_docstring" module="test_lib.example" heading_level="3">
<SigArgSection>
<SigArg name="param1" /><SigArg name="param2" />
</SigArgSection>
<Description summary="Example function with types documented in the docstring." extended_summary="`PEP 484`_ type annotations are supported. If attribute, parameter, and\nreturn types are annotated according to `PEP 484`_, they do not need to be\nincluded in the docstring:" />
<ParamSection name="Parameters">
	<Parameter name="param1" type="int" desc="The first parameter. something something\nsecond line. foo" />
	<Parameter name="param2" type="str" desc="The second parameter." />
</ParamSection>
<ParamSection name="Returns">
	<Parameter type="bool" desc="True if successful, False otherwise." />
</ParamSection>
</DocSection>