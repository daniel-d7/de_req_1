import unittest
import pandas as pd
from modules import transform

class TestTransformFunction(unittest.TestCase):
    def setUp(self):
        # Sample test data
        self.sample_data = pd.read_csv("./raw/data_test.csv")

    def test_salary_parsing(self):
        transformed = transform(self.sample_data)
        
        # Test VND salary range
        self.assertEqual(transformed.iloc[0]["min_salary"], 10000000)
        self.assertEqual(transformed.iloc[0]["max_salary"], 20000000)
        self.assertEqual(transformed.iloc[0]["salary_currency"], "VND")
        
        # Test no salary range
        self.assertEqual(transformed.iloc[2]["min_salary"], 0)
        self.assertEqual(transformed.iloc[2]["max_salary"], 35000000)
        self.assertEqual(transformed.iloc[2]["salary_currency"], "VND")
        
        # Test max salary
        self.assertEqual(transformed.iloc[3]["min_salary"], 0)
        self.assertEqual(transformed.iloc[3]["max_salary"], 0)
        self.assertEqual(transformed.iloc[3]["salary_currency"], "VND")
        
        # Test min salary in USD
        self.assertEqual(transformed.iloc[4]["min_salary"], 1700)
        self.assertEqual(transformed.iloc[4]["max_salary"], 0)
        self.assertEqual(transformed.iloc[4]["salary_currency"], "USD")

        # Test max salary in USD
        self.assertEqual(transformed.iloc[5]["min_salary"], 0)
        self.assertEqual(transformed.iloc[5]["max_salary"], 1800)
        self.assertEqual(transformed.iloc[5]["salary_currency"], "USD")

    def test_address_splitting(self):
        transformed = transform(self.sample_data)
        
        # Test Hà Nội address
        hn_rows = transformed[transformed["province"] == "Hà Nội"]
        self.assertEqual(len(hn_rows), 10)
        self.assertIn("Cầu Giấy", hn_rows["district"].values)
        self.assertIn("Ba Đình", hn_rows["district"].values)
        
        # Test Hồ Chí Minh address
        hcm_rows = transformed[transformed["province"] == "Hồ Chí Minh"]
        self.assertEqual(len(hcm_rows), 4)
        self.assertIn("Quận 7", hcm_rows["district"].values)
        self.assertIn("Quận 9", hcm_rows["district"].values)
        
        # Test Toàn Quốc address
        country_rows = transformed[transformed["province"] == "Toàn Quốc"]
        self.assertGreater(1, len(country_rows))  # Should not exists
        
        # Test Đà Nẵng with "All" district
        dn_rows = transformed[transformed["province"] == "Đà Nẵng"]
        self.assertGreater(len(dn_rows), 1)  # Should be expanded to all districts of Đà Nẵng

    def test_empty_address(self):
        data = self.sample_data.copy()
        data.at[0, "address"] = None
        transformed = transform(data)
        self.assertEqual(len(transformed), 0)

    def test_invalid_salary_format(self):
        data = self.sample_data.copy()
        data.at[0, "salary"] = "Invalid salary format"
        with self.assertRaises(Exception):
            transform(data)

    def test_output_columns(self):
        transformed = transform(self.sample_data)
        expected_columns = [
            'created_date', 'job_title', 'company', 'salary', 'province', 
            'district', 'time', 'link_description', 'min_salary', 
            'max_salary', 'salary_currency'
        ]
        self.assertListEqual(list(transformed.columns), expected_columns)

    def test_edge_cases(self):
        # Test with "Nước Ngoài" province
        data = self.sample_data.copy()
        transformed = transform(data)
        self.assertEqual(transformed.iloc[-1]["province"], "Nước Ngoài")

if __name__ == "__main__":
    unittest.main()