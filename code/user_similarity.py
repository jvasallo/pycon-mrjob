from mrjob.job import MRJob
from mrjob.protocol import JSONValueProtocol

def jaccard(xs, ys):
    return float(len(set(xs) & set(ys))) / len(set(xs) | set(ys))

class UserSimilarity(MRJob):
    INPUT_PROTOCOL = JSONValueProtocol


    def user_biz_extract(self, _, record):
       # only get type rviews
       if record['type'] == 'review':
           # from that one record return the user and business id
           yield record['user_id'], record['business_id']

    # we have a user id and a business that we need to reduce from above
    def define_user(self, user_id, biz_ids):
        #print list(set(biz_ids))
        # reduces to a user id and a list of businesses
        yield user_id, list(set(biz_ids))

    # pass down a user id and a list of businesses and out put the business and a list of user and business ids
    def find_possible(self, user_id, biz_ids):
        for biz in biz_ids:
            yield biz, [user_id, biz_ids]

###############STUCK HERE####################################
    def calculate_jaccard(self, biz_id, user_defs):
        all_user_defs = list(user_defs)
        for i, user_def in enumerate(all_user_defs):
            for compare_def in all_user_defs[i+1:]:
                score = jaccard(user_def[1], compare_def[1])
                if score >= 0.5:
                    yield [[min(user_def[0], compare_def[0]),
                            max(user_def[0], compare_def[0])],
                           score]

    def unique_user(self, user_pair, scores):
        yield user_pair, scores.next()
###########################END STUCK##########################

    ###
    # TODO: write the functions needed to
    # 1) find potential matches, 
    # 2) calculate the Jaccard between users, with a user defined as a set of
    # reviewed businesses
    ##/

    def steps(self):
        """TODO: Document what you expect each mapper and reducer to produce:
        mapper1: <line, record> => <key, value>
        reducer1: <key, [values]>
        mapper2: ...
        """
        return [self.mr(mapper=self.user_biz_extract, reducer=self.define_user),
                self.mr(mapper=self.find_possible, reducer=self.calculate_jaccard),
                self.mr(reducer=self.unique_user)]


if __name__ == '__main__':
    UserSimilarity.run()
