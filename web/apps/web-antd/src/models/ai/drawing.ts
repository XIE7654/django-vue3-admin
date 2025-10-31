import { BaseModel } from '#/models/base';

export namespace DrawingApi {
  export interface Drawing {
    id: number;
    remark: string;
    creator: string;
    modifier: string;
    update_time: string;
    create_time: string;
    is_deleted: boolean;
  }
}

export class DrawingModel extends BaseModel<DrawingApi.Drawing> {
  constructor() {
    super('/ai/drawing/');
  }
}
