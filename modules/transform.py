import pandas as pd

def transform(data):
    #Salary normalize into 3 field including min_salary, max_salary, salary_currency
    salary_list = data["salary"].to_list()
    min_salary = []
    max_salary = []
    salary_currency = []
    for i in salary_list:
        if i is None:
            min_salary.append(None)
            max_salary.append(None)
            salary_currency.append(None)
        else:
            if i == "Thoả thuận":
                min_salary.append(0)
                max_salary.append(0)
                salary_currency.append("VND")
            elif "USD" in i:
                salary_currency.append("USD")
                if not "-" in i:
                    if "Tới" in i:
                        min_salary.append(0)
                        words_list = i.replace(",", "").split()
                        salary_list = [next(int(ii) for ii in words_list if ii.isdigit())]
                        max_salary.append(int(salary_list[0]))
                    else:
                        max_salary.append(0)
                        words_list = i.replace(",", "").split()
                        salary_list = [next(int(ii) for ii in words_list if ii.isdigit())]
                        min_salary.append(int(salary_list[0]))
                else:
                    words_list = i.replace(",", "").split()
                    salary_list = [ii for ii in words_list if ii.isdigit()]
                    if len(salary_list) >= 2:
                        if salary_list[0] < salary_list[1]:
                            min_salary.append(salary_list[0])
                            max_salary.append(salary_list[1])
                        else:
                            min_salary.append(salary_list[1])
                            max_salary.append(salary_list[0])
                    else:
                        min_salary.append(None)
                        max_salary.append(None)
            else:
                salary_currency.append("VND")
                if not "-" in i:
                    min_salary.append(0)
                    words_list = i.lower().split()
                    salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                    if "triệu" in words_list:
                        max_salary.append(int(salary_list[0]*1000000))
                    else:
                        max_salary.append(int(salary_list[0]))
                else:
                    words_list = i.split()
                    salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                    if "triệu" in words_list:
                        salary_list = [float(ii)*1000000 for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                    else:
                        salary_list = [float(ii) for ii in words_list if any([ii.replace(".", "", 1).isdigit(), ii.isdigit()])]
                    if salary_list[0] < salary_list[1]:
                            min_salary.append(int(salary_list[0]))
                            max_salary.append(int(salary_list[1]))
                    else:
                            min_salary.append(int(salary_list[1]))
                            max_salary.append(int(salary_list[0]))
    data["min_salary"] = [x for x in min_salary]
    data["max_salary"] = [x for x in max_salary]
    data["salary_currency"] = [x for x in salary_currency]
    #Pre-defined all provinces
    provinces = ["An Giang", "Bà Rịa - Vũng Tàu", "Bạc Liêu", "Bắc Giang", "Bắc Kạn", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang", "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hải Phòng", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hoà", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Phú Yên", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị", "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Hà Nội", "Hồ Chí Minh", "Đà Nẵng", "Cần Thơ"]
    rows = []
    for i, row in data.iterrows():
        address = row["address"]
        if pd.isna(address):
            return []
        
        parts = [part.strip() for part in address.split(':')]
        pairs = []
        
        if not parts:
            return []
        
        current_province = parts[0]
        i = 1  # Start from the first part after province
        
        while i < len(parts):
            part = parts[i]
            
            # Check if this part is a new province
            if part in provinces:
                # If we have current province without districts, add it
                if not any(p[0] == current_province for p in pairs):
                    pairs.append((current_province, "All"))
                current_province = part
                i += 1
            else:
                # Process all consecutive non-province parts as districts
                districts = []
                while i < len(parts) and parts[i] not in provinces:
                    districts.extend([d.strip() for d in parts[i].split(',') if d.strip()])
                    i += 1
                
                # Add province-district pairs
                for district in districts:
                    pairs.append((current_province, district))
        
        # Add the last province if it wasn't added
        if not any(p[0] == current_province for p in pairs):
            pairs.append((current_province, "All"))
                
        for province, district in pairs:
            new_row = row.to_dict()
            new_row['province'] = province
            new_row['district'] = district
            rows.append(new_row)
    address_splited_data = pd.DataFrame(rows)
    columns = ['created_date', 'job_title', 'company', 'salary', 'province', 'district', 'time', 'link_description', "min_salary", "max_salary", "salary_currency"]
    address_splited_data = address_splited_data[columns]
    #Load full province_district to normalize All district case
    province_district = pd.read_csv("./raw/vietnam_administrative_units.csv").loc[:,["province", "district"]].drop_duplicates()
    joined_data_province_all = pd.merge(
        address_splited_data[(address_splited_data["district"] == "All") & (address_splited_data["province"] != "Toàn Quốc") & (address_splited_data["province"] != "Nước Ngoài")],
        province_district,
        on = "province",
        how = "left",
        suffixes = ("", "_second")
    )
    joined_data_country = pd.merge(
        address_splited_data[address_splited_data["province"] == "Toàn Quốc"],
        province_district[:]["district"],
        how = "cross",
        suffixes = ("", "_second")
    )
    joined_data_country_all = pd.merge(
        joined_data_country,
        province_district,
        on = "district",
        how = "left",
        suffixes = ("", "_second")
        )
    oversea = address_splited_data[address_splited_data["province"] == "Nước Ngoài"]
    joined_data_province_all = joined_data_province_all.drop(columns=["district"]).rename(columns={"district_second":"district"}).reindex(columns=['created_date', 'job_title', 'company', 'salary', 'province', 'district', 'time', 'link_description', "min_salary", "max_salary", "salary_currency"])
    joined_data_country_all = joined_data_country_all.drop(columns=["district","province"]).rename(columns={"district_second":"district","province_second":"province"}).reindex(columns=['created_date', 'job_title', 'company', 'salary', 'province', 'district', 'time', 'link_description', "min_salary", "max_salary", "salary_currency"])
    filtered = address_splited_data[~((address_splited_data["province"] == "Toàn Quốc") | (address_splited_data["district"] == "All") | (address_splited_data["district"] == "Nước Ngoài"))]
    merged_data = pd.concat([address_splited_data[~((address_splited_data["district"] == "All") | (address_splited_data["province"] == "Toàn Quốc") | (address_splited_data["province"] == "Nước Ngoài"))], joined_data_country_all, joined_data_province_all, oversea], ignore_index=True)
    
    return merged_data