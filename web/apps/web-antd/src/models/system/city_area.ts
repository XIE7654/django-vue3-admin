import { BaseModel } from '#/models/base';

export namespace SystemCityAreaApi {
  export interface SystemCityArea {
    id: number;
    remark: string;
    creator: string;
    modifier: string;
    update_time: string;
    create_time: string;
    is_deleted: boolean;
    prov_id: number;
    prov_name: string;
    city_id: number;
    city_name: string;
    area_id: number;
    area_name: string;
  }
}

export class SystemCityAreaModel extends BaseModel<SystemCityAreaApi.SystemCityArea> {
  constructor() {
    super('/system/city_area/');
  }
}
