<script lang="ts" setup>
import {
  ACTION_ICON,
  type OnActionClickParams, TableAction,
  type VxeTableGridOptions,
} from '#/adapter/vxe-table';
import type { SystemDictDataApi } from '#/api/system/dict_data';

import { useRoute } from 'vue-router';

import { Page, useVbenModal } from '@vben/common-ui';
import { Plus } from '@vben/icons';

import { Button, message } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';
import { deleteDictData, getDictDataList } from '#/api/system/dict_data';
import { $t } from '#/locales';

import { useColumns } from './data';
import Form from './modules/form.vue';

const route = useRoute();
const [FormModal, formModalApi] = useVbenModal({
  connectedComponent: Form,
  destroyOnClose: true,
});

/**
 * 编辑字典数据
 * @param row
 */
function onEdit(row: SystemDictDataApi.SystemDictData) {
  if (row.menu_ids) {
    row.menu_ids = row.menu_ids.split(',').map(Number);
  }
  formModalApi.setData(row).open();
}

/**
 * 创建字典数据
 */
function onCreate() {
  formModalApi
    .setData({
      dict_type: Number(route.query.dict_type),
    })
    .open();
}

/**
 * 删除字典数据
 * @param row
 */
function onDelete(row: SystemDictDataApi.SystemDictData) {
  const hideLoading = message.loading({
    content: $t('ui.actionMessage.deleting', [row.name]),
    duration: 0,
    key: 'action_process_msg',
  });
  deleteDictData(row.id)
    .then(() => {
      message.success({
        content: $t('ui.actionMessage.deleteSuccess', [row.name]),
        key: 'action_process_msg',
      });
      refreshGrid();
    })
    .catch(() => {
      hideLoading();
    });
}

/**
 * 表格操作按钮的回调函数
 */
function onActionClick({
  code,
  row,
}: OnActionClickParams<SystemDictDataApi.SystemDictData>) {
  switch (code) {
    case 'delete': {
      onDelete(row);
      break;
    }
    case 'edit': {
      onEdit(row);
      break;
    }
  }
}

const [Grid, gridApi] = useVbenVxeGrid({
  gridEvents: {},
  gridOptions: {
    columns: useColumns(onActionClick),
    height: 'auto',
    keepSource: true,
    pagerConfig: {
      enabled: true,
    },
    proxyConfig: {
      ajax: {
        query: async ({ page }, formValues) => {
          const { dict_type } = route.query;
          return await getDictDataList({
            page: page.currentPage,
            pageSize: page.pageSize,
            dict_type,
            ...formValues,
          });
        },
      },
    },
    toolbarConfig: {
      custom: true,
      export: false,
      refresh: { code: 'query' },
      zoom: true,
    },
    treeConfig: {
      parentField: 'pid',
      rowField: 'id',
      transform: false,
    },
  } as VxeTableGridOptions,
});

/**
 * 刷新表格
 */
function refreshGrid() {
  gridApi.query();
}
</script>
<template>
  <Page auto-content-height>
    <FormModal @success="refreshGrid" />
    <Grid table-title="字典数据">
      <template #toolbar-tools>
        <TableAction
          :actions="[
            {
              label: $t('ui.actionTitle.create', [$t('system.dict_data.name')]),
              type: 'primary',
              icon: ACTION_ICON.ADD,
              auth: ['system:dict_data:create'],
              onClick: onCreate,
            },
          ]"
        />
      </template>
    </Grid>
  </Page>
</template>
