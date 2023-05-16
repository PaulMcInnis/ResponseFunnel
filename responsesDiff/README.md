## Collection Responses JSON Diff

To compare two sets of `responses` folders between eachother, you can use the included `diff.py` script.

This is intended to be used with the folder outputs of JSON from the `responsesToFile` tool.


    usage: diff.py [-h] folder_a folder_b output

    compare two folders of reponse .JSON to identify sync issues.

    positional arguments:
      folder_a    Folder of per-endpoint reponse JSON to compare against.
      folder_b    Folder of per-endpoint reponse JSON to compare with.
      output      Folder to store per-endpoint diffs (HTML)

    options:
      -h, --help  show this help message and exit


Install requirements via `pip install -r requirements.txt`

This will generate interactive diffs using `jcym` which is helpful when identifying synchronization issues between servers. The workflow is like this:

1. create a collection in postman to hit all of your endpoints
1. add the following to your collection `test`

   ```
   if (pm.environment.get('dumpJson') === 'true') {
       let opts = {
           requestName: request.name || request.url,
           fileExtension: 'json',
           mode: 'writeFile',
           uniqueIdentifier: false,
           responseData: pm.response.text()
       };
       pm.sendRequest({
           url: 'http://localhost:3000/write',
           method: 'POST',
           header: 'Content-Type:application/json',
           body: {
               mode: 'raw',
               raw: JSON.stringify(opts)
           }
       }, function (err, res) {
           console.log(res);
       });
   }
   ```

1. create an environment for local use with this server, and within that environment define `dumpJson` and set it to `true`.
1. if you have other existing environments, i.e. ones used with Postman's `Monitor`, make sure you set `dumpJson` to `false` to avoid errors in console / false appearance of health issues due to attempting to reach `localhost:3000`
1. start the server
1. run the collection on server A with `dumpJson` `true` in Postman
1. `cp -r ./responses responsesA`
1. switch to a collection on server B with `dumpJson` `true`, and run in Postman (use a VPN if needed)
1. `cp -r ./responses responsesB`
1. run the comparison `python3 diff.py ./responsesA ./responsesB ./diffAB`. _NOTE: interactive diffs will be created only if there are differences to view_
1. view any interactive diffs created, in `./diffAB/<response-name>.json>/index.html`, and the raw diff output in `./diffAB/raw-diffs.txt`
