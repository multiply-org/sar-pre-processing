# import snappy

class DummySARPreProcessor:

    def pre_process(self, sar_data):
        print ('Performing pre-processing on SAR data')
        # return snappy.Product('pre_processed_sar_data', 'pre_processed_sar_data', 1, 1)
        return 'pre_processed_sar_product'