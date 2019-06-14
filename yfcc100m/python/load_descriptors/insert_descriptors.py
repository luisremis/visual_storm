# This files assumes that the images are already inserted,
# with the ID property set as a int, matching the descriptors ID.

import vdms

import descriptors_reader as dr

descriptor_set_name = "hybridNet"

def insert_descriptor_set(db):

    iDS = { "AddDescriptorSet" : {

            "name": descriptor_set_name,
            "dimensions": 4096,
            "engine": "FaissIVFFlat",
            "metric": "L2"
        }
    }

    allqueries = []
    allqueries.append(iDS)

    db.query(allqueries)

    print(db.get_last_response_str())

# This method is paralelizable, can be called multiple times
def insert_descriptors(batch_size, ids, descriptors, db):

    # rounds = int(len(ids) / batch_size)
    rounds = len(ids)

    print("rounds:", rounds)

    print("n_ids:", len(ids))
    print("n_descriptors:", len(descriptors))

    for round_n in range(rounds):

        # start = round_n * batch_size
        # end   = min(start + batch_size, len(ids))

        start = round_n
        end = round_n + 1

        ref_counter = 1

        all_queries = []
        blobs = []

        for i in range(start,end):

            print("inderting desc id:", ids[i])

            fI = { "FindImage": {
                    "_ref": ref_counter,
                    "constraints": {
                        "ID": ["==", ids[i]]
                    },
                    "unique": True,
                    "results": {
                        "blob": False # Avoid returning the image blobe
                    }
                }
            }

            aD = { "AddDescriptor": {

                    "set": descriptor_set_name,

                    "link": {
                        "ref": ref_counter
                    }
                }
            }

            all_queries.append(fI)
            all_queries.append(aD)

            blobs.append(descriptors[i])

            ref_counter += 1

        respones, blob = db.query(all_queries, [blobs])

        print(db.get_last_response_str())

def main():

    db = vdms.vdms()
    db.connect("localhost", 55559)

    insert_descriptor_set(db)

    prefix = "/nvme4/YFCC100M_hybridCNN_gmean_fc6_"
    d_reader = dr.descriptors_reader(prefix)

    total = 1000000
    batch_size = 1000

    inserted = 0

    while inserted < total:

        ids, desc = d_reader.get_next_n(batch_size)

        insert_descriptors(batch_size, ids, desc, db)

        inserted += batch_size

        print("Elements Inserted: ", inserted)

    # Read from file, this should read the files as needed, given a number
    # of elements, it should open the different files as needed.

    # Loop over the total.


if __name__ == "__main__":

    main()


