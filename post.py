import os
import subprocess

KEY = os.environ["KEY"]

url = "https://api.estuary.tech/content/add"
aut = f'"Authorization: Bearer {KEY}"'
con = '"Content-Type: multipart/form-data"'
dat = '"data=@/home/oscar/Escritorio/test3.json"'

post = f'curl -X POST {url} -H {aut} -H {con} -F {dat}'

resp = subprocess.run(post,
                      stderr=subprocess.PIPE,
                      stdout=subprocess.PIPE,
                      text=True,
                      shell=True)

print(resp.stdout)

str({"cid":"bafkreialmz7zxqugptwwtaz54jbalyy5phvheirhpmqposklb74i6ilsja",
 "retrieval_url":"https://dweb.link/ipfs/bafkreialmz7zxqugptwwtaz54jbalyy5phvheirhpmqposklb74i6ilsja",
 "estuaryId":49229648,
 "providers":["/ip4/145.40.93.107/tcp/6745/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/127.0.0.1/tcp/6745/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/145.40.93.107/udp/6746/quic/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/127.0.0.1/udp/6746/quic/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/145.40.93.107/tcp/6747/ws/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/127.0.0.1/tcp/6747/ws/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/100.122.184.192/tcp/6745/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/100.104.120.192/tcp/6745/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7",
              "/ip4/100.97.164.64/tcp/6745/p2p/12D3KooWBUriTeu6YoJsuSg5gCvEecim9xKdZaW8fE54LUzmWJn7"]})
