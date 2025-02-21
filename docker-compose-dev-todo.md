TODO:
- [ ] popiši kaj rabiš pognat da solr vraša podatke po tem ko bazo importaš
- [ ] fix parlacards dev
  - trenutno zbuilda samo enkrat in nima live reload in nič dev serverja ne požene
  - to da je v env vars treba napisat interno docker domeno (http://parlasite:8000, http://parlacards:3000, itd.) in fajn ker hoče v browserju iste urlje klicat in pol tam crknejo
  - treba je mountat parlacards/dist folder v parlacards in parlassets folder kar ni ok, ker se tam servirajo built fajli
  - cors ma probleme in ne dela javascript v karticah


- rad bi združil vse fronend containerje v enega (parlafront) kar sem že začel delat 2022 in nikoli končal, prvi task tu je zrihtat parlasite migracijo v ESM (glej branch `dev-parlasite-esm`), potem pa bi rad serviral parlasite in parlacards iz istega serverja (v dev pa tudi parlassets, ker bo nginx samo ko se deploya)

- when merging to k8s branches fix/check that it doesnt break bacause of new config values in parlasite config (you need to add new env vars to deployment.yaml)
