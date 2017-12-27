# Search API

This page documents the REST API that we will provide to allow apps to use our
search engine. 

Our REST API will have a single endpoint.

## `GET /results`

This endpoint requires the following query paramenters

- `query=` : A string specifying the query for the database
- `from=` : How deep to page into the results. If left off, assumed
  to be `0`.

Queries can return massive amounts of results and returning them all in a single
query may be problematic. In addition, an interface for this would probably only
want to display the first few results so downloading all of them would be a
waste of bandwidth. Our endpoint therefore only returns 10 results at a time. To
fetch the first page of results simply send the query, to fetch the second use
read the `nextFrom` and use it to set the `from` query param on the next call.

The response will be JSON containing the following keys:

- `nextFrom`: If there are additional pages, this will be the value of `from` to use
  on a subsequent request in order to get the next page. If there is not a next page,
  will be `null`. When not null, it is a string.
- `prevFrom`: If the request was not for the first page, this will refer to the `from`
   value needed to fetch the previous page. When not null, it is a string.
- `results`: An array of objects describing one search result. There will be at
  most 10 elements in this list. Each of these objects has the following keys
  - `title`: The title of the page being linked to
  - `link`: The full URL to the page
  - `snippet`: A string pulled from the contents of the page
  
Example request:
```
GET http://localhost:80/results?query=example?from=2,
```

Example response:

```json
{
 "prevFrom": "1",
 "nextFrom": "3",
 "results":
 [
   {
     "title": "This is a page",
     "link": "http://example.com/index.html",
     "snippet": "This domain is established to be used for illustrative examples"
   },
   { ... },
   { ... },
   { ... },
   { ... },
   { ... },
   { ... },
   { ... },
   { ... },
   { ... }
 ]
}
```
