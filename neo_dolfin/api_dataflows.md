```mermaid
sequenceDiagram
    loop Daily query
        User->>Dolfin: Hello Dolfin, how are you?
        alt is sick
            Dolfin->>User: Not so good :(
        else is well
            Dolfin->>User: Feeling fresh like a daisy
        end

        opt Extra response
            Dolfin->>User: Thanks for asking
        end
    end
```
