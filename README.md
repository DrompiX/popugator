# Task tracker for Popugs
This repository was created as a homework solution for [course in Async Architecture](https://education.borshev.com/architecture)


## Design
Event storming, data & domain models, services and event descriptions are [located here](https://miro.com/app/board/uXjVPR1YWZA=/?moveToWidget=3458764534854874499&cot=14)

## Simplifications

### General
1. No database migrations
1. Single database instance for all services, but separate databases inside

### Gateway API (+auth)
1. Simplest auth by bearer token, which equals to registered username \
If user was registered with username `test_user`, then token auth should 
have a header `Authorization: Bearer test_user`
