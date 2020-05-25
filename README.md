# Python SSB Example

Scuttlebutt should be fun and easy to implement in lots of languages. I'm bad
at Python, which makes it an excellent language for testing implementation
difficulty.

Pairs well with [HTTP-SSB](https://github.com/christianbundy/http-ssb) for testing.

```shell
python3 main.py | curl --header 'Content-Type: application/json' --data '@-' "localhost:3000"
```

## License 

AGPL-3.0
