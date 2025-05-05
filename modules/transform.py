import pandas as pd

def transform(data):
    #Salary normalize into 3 field including min_salary, max_salary, salary_currency
    salary_list = data["salary"].to_list()
    min_salary = []
    max_salary = []
    salary_currency = []
    for i in salary_list:
        if i == "Thoả thuận":
            min_salary.append(0)
            max_salary.append(0)
            salary_currency.append("VND")
        elif "USD" in i:
            salary_currency.append("USD")
            if not "-" in i:
                min_salary.append(0)
                words_list = i.replace(",", "").split()
                salary_list = [float(next(ii for ii in words_list if ii.isdigit()))]
                max_salary.append(salary_list[0])
            else:
                words_list = i.replace(",", "").split()
                salary_list = [float(ii) for ii in words_list if ii.isdigit()]
                if salary_list[0] < salary_list[1]:
                    min_salary.append(salary_list[0])
                    max_salary.append(salary_list[1])
                else:
                    min_salary.append(salary_list[1])
                    max_salary.append(salary_list[0])
        else:
            salary_currency.append("VND")
            if not "-" in i:
                min_salary.append(0)
                words_list = i.lower().split()
                salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                if "triệu" in words_list:
                    max_salary.append(salary_list[0]*1000000)
                else:
                    max_salary.append(salary_list[0])
            else:
                words_list = i.split()
                salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                if "triệu" in words_list:
                    salary_list = [float(ii)*1000000 for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                else:
                    salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                if salary_list[0] < salary_list[1]:
                        min_salary.append(salary_list[0])
                        max_salary.append(salary_list[1])
                else:
                        min_salary.append(salary_list[1])
                        max_salary.append(salary_list[0])
    data["min_salary"] = [x for x in min_salary]
    data["max_salary"] = [x for x in max_salary]
    data["salary_currency"] = [x for x in salary_currency]
    #Pre-defined all provinces
    provinces = ["An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ", "Nước ngoài"]
    rows = []
    for i, row in data.iterrows():
        address = row["address"]
        if pd.isna(address):
            return []
        parts = [part.strip() for part in address.split(':')]
        pairs = []
        i = 0
        while i < len(parts):
            current = parts[i]
            if current in provinces:
                province = current
                if i + 1 < len(parts) and parts[i + 1] not in provinces:
                    district = parts[i + 1]
                    i += 2
                else:
                    district = "All"
                    i += 1
                pairs.append((province, district))
            else:
                if pairs:
                    last_province, last_district = pairs[-1]
                    if last_district is None:
                        pairs[-1] = (last_province, current)
                i += 1
        for province, district in pairs:
            new_row = row.to_dict()
            new_row['province'] = province
            new_row['district'] = district
            rows.append(new_row)
    address_splited_data = pd.DataFrame(rows)
    columns = ['created_date', 'job_title', 'company', 'salary', 'province', 'district', 'time', 'link_description']
    address_splited_data = address_splited_data[columns]
    #Load full province_district to normalize All district case
    province_district = pd.read_csv("./raw/vietnam_administrative_units.csv").loc[:,["province", "district"]].drop_duplicates()
    merged_data = pd.merge(
        address_splited_data[address_splited_data["district"] == "All"],
        province_district,
        on = "province",
        how = "left",
        suffixes = ("", "_second")
    )
    merged_data = merged_data.drop("district", axis=1).rename(columns={"district_second":"district"})
    return merged_data