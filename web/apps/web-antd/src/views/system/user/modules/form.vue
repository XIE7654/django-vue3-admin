<script lang="ts" setup>
import type { SystemUserApi } from '#/models/system/user';

import { computed, ref } from 'vue';

import { useVbenModal } from '@vben/common-ui';

import { Button } from 'ant-design-vue';

import { useVbenForm } from '#/adapter/form';
import { $t } from '#/locales';
import { SystemConfigModel } from '#/models/system/config';
import { SystemUserModel } from '#/models/system/user';

import { useSchema } from '../data';

const emit = defineEmits(['success']);

const formModel = new SystemUserModel();
const systemConfigModel = new SystemConfigModel();

const formData = ref<SystemUserApi.SystemUser>();
const getTitle = computed(() => {
  return formData.value?.id
    ? $t('ui.actionTitle.edit', [$t('system.user.name')])
    : $t('ui.actionTitle.create', [$t('system.user.name')]);
});

const [Form, formApi] = useVbenForm({
  layout: 'horizontal',

  commonConfig: {
    colon: true,
    formItemClass: 'col-span-2 md:col-span-1',
  },
  wrapperClass: 'grid-cols-2 gap-x-4',
  schema: useSchema(),
  showDefaultActions: false,
});

function resetForm() {
  formApi.resetForm();
  formApi.setValues(formData.value || {});
}

const [Modal, modalApi] = useVbenModal({
  async onConfirm() {
    const { valid } = await formApi.validate();
    if (valid) {
      modalApi.lock();
      const data = await formApi.getValues();
      try {
        await (formData.value?.id
          ? formModel.update(formData.value.id, data)
          : formModel.create(data));
        await modalApi.close();
        emit('success');
      } finally {
        modalApi.lock(false);
      }
    }
  },
  onOpenChange(isOpen) {
    if (isOpen) {
      const data = modalApi.getData<SystemUserApi.SystemUser>();
      const isEmptyObject =
        data &&
        typeof data === 'object' &&
        !Array.isArray(data) &&
        Object.keys(data).length === 0;

      if (data && !isEmptyObject) {
        formData.value = data;
        formApi.setValues(formData.value);
      } else {
        // 新建时，从系统配置读取默认初始密码
        systemConfigModel
          .list({ key: 'sys.user.initPassword' } as any)
          .then((resp: any) => {
            const items = resp?.items ?? (Array.isArray(resp) ? resp : []);
            const initPwd = items?.[0]?.value;
            if (initPwd) {
              formApi.setValues({ password: initPwd });
            }
          })
          .catch(() => {});
      }
    }
  },
});
</script>

<template>
  <Modal :title="getTitle" class="w-full max-w-[800px]">
    <Form />
    <template #prepend-footer>
      <div class="flex-auto">
        <Button type="primary" danger @click="resetForm">
          {{ $t('common.reset') }}
        </Button>
      </div>
    </template>
  </Modal>
</template>
<style lang="css" scoped></style>
