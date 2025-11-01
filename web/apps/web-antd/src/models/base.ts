import type { Recordable } from '@vben/types';

import type { ExtendedModalApi } from '@vben-core/popup-ui';

import { message } from 'ant-design-vue';

import { requestClient } from '#/api/request';

export interface CoreModel {
  remark: string;
  creator: string;
  modifier: string;
  update_time: string;
  create_time: string;
  is_deleted: boolean;
}

// 通用Model基类
export class BaseModel<
  T,
  CreateData = Omit<T, any>,
  UpdateData = Partial<CreateData>,
> {
  protected baseUrl: string;
  protected formModalApi: ExtendedModalApi | undefined;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  /**
   * 通用操作方法
   * @param url 操作路径
   * @param data 请求数据
   * @param id 是否针对单条记录的操作
   * @param method 请求方法
   */
  async action(
    url: string,
    data: any = {},
    id: null | number = null,
    method = 'post',
  ) {
    const baseUrl = id
      ? `${this.baseUrl}${id}/${url}/`
      : `${this.baseUrl}${url}/`;

    const config =
      method === 'get'
        ? {
            url: baseUrl,
            method: 'get',
            params: data,
          }
        : {
            url: baseUrl,
            method,
            data,
          };

    return requestClient.request(url, config);
  }

  /**
   * 创建记录
   */
  async create(data: CreateData) {
    return requestClient.post(this.baseUrl, data);
  }

  /**
   * 删除记录
   */
  async delete(id: number) {
    return requestClient.delete(`${this.baseUrl}${id}/`);
  }

  /**
   * 导出数据
   */
  async export(params: Recordable<T> = {}) {
    return requestClient.get(`${this.baseUrl}export/`, {
      params,
      responseType: 'blob', // 二进制流
    });
  }

  /**
   * 获取列表数据
   */
  async list(params: Recordable<T> = {}) {
    return requestClient.get<Array<T>>(this.baseUrl, { params });
  }

  onDelete<T extends { id: number }>(row: T, refreshGrid: () => void) {
    const hideLoading = message.loading({
      content: '删除中...',
      duration: 0,
      key: 'action_process_msg',
    });
    this.delete(row.id)
      .then(() => {
        message.success({
          content: '删除成功',
          key: 'action_process_msg',
        });
        refreshGrid();
      })
      .catch(() => {
        hideLoading();
      });
  }

  onEdit(row: T) {
    this.formModalApi?.setData(row).open();
  }

  /**
   * 部分更新记录
   */
  async patch(id: number, data: Partial<UpdateData>) {
    return requestClient.patch(`${this.baseUrl}${id}/`, data);
  }

  /**
   * 获取单条记录
   */
  async retrieve(id: number) {
    return requestClient.get<T>(`${this.baseUrl}${id}/`);
  }

  setFormModalApi(api: ExtendedModalApi) {
    this.formModalApi = api;
  }
  /**
   * 全量更新记录
   */
  async update(id: number, data: UpdateData) {
    return requestClient.put(`${this.baseUrl}${id}/`, data);
  }
}
//
// // 字典类型专用Model
// export class SystemDictTypeModel extends BaseModel<SystemDictTypeApi.SystemDictType> {
//   constructor() {
//     super('/system/dict_type/');
//   }
// }
//
// // AmazonListingModel示例
// export class AmazonListingModel extends BaseModel<AmazonListing> {
//   constructor() {
//     super('amazon/amazon_listing/');
//   }
// }
// const dictTypeModel = new SystemDictTypeModel();
//
// // 获取列表
// dictTypeModel.list().then(({ data }) => console.log(data));
//
// // 创建记录
// dictTypeModel.create({ name: '新字典', type: 'new_type' });
//
// // 更新记录
// dictTypeModel.patch('123', { name: '更新后的字典' });
