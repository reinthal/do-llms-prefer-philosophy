
### Tool call: browser_snapshot
- Args
```json
{}
```
- Snapshot: 001.snapshot.yml


### Tool call: browser_navigate
- Args
```json
{
  "url": "https://en.wikipedia.org"
}
```
- Code
```js
await page.goto('https://en.wikipedia.org');
```
- Snapshot: 002.snapshot.yml


### Tool call: browser_close
- Args
```json
{}
```
- Code
```js
await page.close()
```

