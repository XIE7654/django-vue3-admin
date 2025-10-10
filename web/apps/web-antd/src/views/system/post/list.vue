<script lang="ts" setup>
import {
  ACTION_ICON,
  type OnActionClickParams, TableAction,
  type VxeTableGridOptions,
} from '#/adapter/vxe-table';
import type { SystemPostApi } from '#/models/system/post';

import { Page, useVbenModal } from '@vben/common-ui';
import { Plus } from '@vben/icons';

import { Button, message } from 'ant-design-vue';

import { useVbenVxeGrid } from '#/adapter/vxe-table';
import { $t } from '#/locales';
import { SystemPostModel } from '#/models/system/post';

import { useColumns, useGridFormSchema } from './data';
import Form from './modules/form.vue';

const formModel = new SystemPostModel();

const [FormModal, formModalApi] = useVbenModal({
  connectedComponent: Form,
  destroyOnClose: true,
});

/**
 * 编辑岗位信息表
 */
function onEdit(row: SystemPostApi.SystemPost) {
  formModalApi.setData(row).open();
}

/**
 * 创建新岗位信息表
 */
function onCreate() {
  formModalApi.setData(null).open();
}

/**
 * 删除岗位信息表
 */
function onDelete(row: SystemPostApi.SystemPost) {
  const hideLoading = message.loading({
    content: '删除岗位信息表',
    duration: 0,
    key: 'action_process_msg',
  });
  formModel
    .delete(row.id)
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

/**
 * 表格操作按钮的回调函数
 */
function onActionClick({
  code,
  row,
}: OnActionClickParams<SystemPostApi.SystemPost>) {
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
  formOptions: {
    schema: useGridFormSchema(),
    submitOnChange: true,
  },
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
          return await formModel.list({
            page: page.currentPage,
            pageSize: page.pageSize,
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
      search: true,
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
    <Grid table-title="岗位信息表">
      <template #toolbar-tools>
        <TableAction
          :actions="[
            {
              label: $t('ui.actionTitle.create', [$t('system.post.name')]),
              type: 'primary',
              icon: ACTION_ICON.ADD,
              auth: ['system:post:create'],
              onClick: onCreate,
            },
          ]"
        />
      </template>
    </Grid>
  </Page>
</template>
