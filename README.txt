#!README

Requirements:
- python 3.11.2
- additional modules
	- psycopg2, pycryptodome
	
Concerns: The table user_logins is set up incorrectly. It casts the app_version as an integer, when it isn't one. I opted to alter the table column to varchar(10), but it does mean it will fail without modifying your own environment.

Questions:

How would you deploy this application in production?
Not entirely sure what you mean. A well executed deployment has a timeline, a test plan with known outcomes, a rollback plan, communication to stakeholders on expected and current status. Presumably the org and by extension the team maintains a versioned repository, and established best practices that one would abide by.

What other components would you want to add to make this production ready?
I'd spend more time pushing parts of it into modules, which would be available to all users who have a need. Good to standardize encryption with controlled access to a key share to users on a need to have basis. Have a dedicated postgres query construction module. Flesh out the comments further with more information about arguments and return values. 

How can this application scale with a growing dataset?
I don't honestly see this approach scaling well with volume. I would be strongly inclined to pursue a different direction, that being a data lake. The application owning team would be responsible for maintaining the unmasked unmodified clear data. As they received data to their master record, they would also be responsible for publishing to the data lake. Multiple copies could be supported, both clear and opaque, with different access rights for each. Then any parties with a justified need could subscribe at their discretion.

How can PII be recovered later on?
The data authority is responsible for maintaining a clear clean data master. That said, this encryption is reversible if you were to store the tag's generated on encryption either in this table or another, as long as the party also had access to the encryption key as well. Note that deterministic encryption which is required to satisfy one of the project's requirements is a bit risky. 

What are the assumptions you made?
The requirements seemed straightforward. The SQS was the most unusual, as I wasn't sure what an SQS should be returning when empty, so I'm not sure if the condition I opted to loop on was ideal. In an actual production environment, I would use boto3 module probably, not recording the output from a CLI run(). Also, that the target postgres table had to be modified to receive app_version without loss of data. That server time would make for an adequate current_date record. One might consider standardizing the metadata timestamps as UTC across the org. 

