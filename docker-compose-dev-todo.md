TODO:
- [ ] popiši kaj rabiš pognat da solr vraša podatke po tem ko bazo importaš
- [ ] fix parlacards dev
  - trenutno zbuilda samo enkrat in nima live reload in nič dev serverja ne požene


- rad bi združil vse fronend containerje v enega (parlafront) kar sem že začel delat 2022 in nikoli končal, prvi task tu je zrihtat parlasite migracijo v ESM (glej branch `dev-parlasite-esm`), potem pa bi rad serviral parlasite in parlacards iz istega serverja (v dev pa tudi parlassets, ker bo nginx samo ko se deploya)

- when merging to k8s branches fix/check that it doesnt break bacause of new config values in parlasite config (you need to add new env vars to deployment.yaml)
