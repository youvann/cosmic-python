# Cosmic python

```sh
python3.8 -m venv .venv && source .venv/bin/activate # or however you like to create virtualenvs
pip install -r requirements.txt
```

## Concept

* Ubiquitous langugage : the business jargon
* Value object pattern : 
    + any domain object that is uniquely identified by the data it holds, we usually make them immutable
    + it does not have a have a long-lived identity
    + For value objects, the hash should be based on all the value attributes, and we should ensure that the objects are immutable. We get this for free by specifying @frozen=True on the dataclass.
    + ex : OrderLine
* Entities : 
    + unlike values, entities have **identity equality**
    + their values can changes and they are still recognizably the same thing
    + ex : Batch
* Domain services : Domain services are not the same thing as the services from the service layer, although they are often closely related. A domain service represents a business concept or process, whereas a service-layer service represents a use case for your application. Often the service layer will call a domain service.
* Dependency Inversion Principle : High level modules (the domain) should not depend on low levels (the infrastructure)
* Repository pattern : a simplifying abstraction over data storage, allowing us to decouple our model layer from the data layer