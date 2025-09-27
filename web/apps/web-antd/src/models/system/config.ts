import { BaseModel } from '#/models/base';

export namespace SystemConfigApi {
  export interface SystemConfig {
    id: number;
    remark: string;
    creator: string;
    modifier: string;
    update_time: string;
    create_time: string;
    is_deleted: boolean;
    name: string;
    key: string;
    value: string;
    config_type: boolean;
  }
}

export class SystemConfigModel extends BaseModel<SystemConfigApi.SystemConfig> {
  constructor() {
    super('/system/config/');
  }
}
