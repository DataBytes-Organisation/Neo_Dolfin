```mermaid
sequenceDiagram
    rect rgb(64,64,64)
    note right of User: A Successful login
        User->>Dolfin_app: Check username and password

        Dolfin_app->>dolfin_db: do you have this username?<br>if yes, does the password match it?

        dolfin_db->>Dolfin_app: send username as session_id<br>send basiq_id to session

        Dolfin_app->>User: Login success!
    end

```
