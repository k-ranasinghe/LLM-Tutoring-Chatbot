# These are the examples used to train SelfQueryRetreiver in chain.py
def get_examples():
    examples = [
    {
        "user_query": "what is bubble sort?",
        "structured_request": 
        """```json
{{
    "query": "bubble sort algorithm implementation and efficiency",
    "filter": "and(eq(\\"subject\\", \\"Programming\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 0,
    },
    {
        "user_query": "explain the process of 3D modeling",
        "structured_request": 
        """```json
{{
    "query": "3D modeling techniques and software",
    "filter": "and(eq(\\"subject\\", \\"3D Design\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 1,
    },
    {
        "user_query": "how do microcontrollers work?",
        "structured_request": 
        """```json
{{
    "query": "microcontroller architecture and programming",
    "filter": "and(eq(\\"subject\\", \\"Electronics\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 2,
    },
    {
        "user_query": "what are the principles of injection molding?",
        "structured_request": 
        """```json
{{
    "query": "injection molding process and materials",
    "filter": "and(eq(\\"subject\\", \\"Manufacturing\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 3,
    },
    {
        "user_query": "explain object-oriented programming concepts",
        "structured_request": 
        """```json
{{
    "query": "object-oriented programming principles and examples",
    "filter": "and(eq(\\"subject\\", \\"Programming\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 4,
    },
    {
        "user_query": "how does 3D printing work?",
        "structured_request": 
        """```json
{{
    "query": "3D printing technologies and processes",
    "filter": "and(eq(\\"subject\\", \\"Manufacturing\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 5,
    },
    {
        "user_query": "what are the basics of circuit design?",
        "structured_request": 
        """```json
{{
    "query": "electronic circuit design principles and components",
    "filter": "and(eq(\\"subject\\", \\"Electronics\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 6,
    },
    {
        "user_query": "explain the concept of recursion in programming",
        "structured_request": 
        """```json
{{
    "query": "recursion in programming with examples and applications",
    "filter": "and(eq(\\"subject\\", \\"Programming\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 7,
    },
    {
        "user_query": "what are the principles of parametric modeling?",
        "structured_request": 
        """```json
{{
    "query": "parametric modeling concepts and software tools",
    "filter": "and(eq(\\"subject\\", \\"3D Design\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 8,
    },
    {
        "user_query": "how does CNC machining work?",
        "structured_request": 
        """```json
{{
    "query": "CNC machining process and programming",
    "filter": "and(eq(\\"subject\\", \\"Manufacturing\\"))"
}}```""",
        "data_source":
        '''```json
{{
    "content": "Brief description of educational content",
    "attributes": {{
        "subject": {{
            "type": "string",
            "description": "The subject relevant to the document. One of \\"Programming\\", \\"Electronics\\", \\"Embedded Systems\\", \\"3D Design\\", \\"Manufacturing\\", \\"Miscellaneous\\" or \\"Other\\"."
        }}
    }}
}}```''',
        "i": 9,
    }
    ]

    return examples