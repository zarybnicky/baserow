<template>
  <div class="filters__value-date">
    <input
      ref="date"
      v-model="dateString"
      type="text"
      class="input filters__value-input"
      :class="{ 'input--error': $v.copy.$error }"
      :placeholder="getDatePlaceholder(field)"
      @focus="$refs.dateContext.toggle($refs.date, 'bottom', 'left', 0)"
      @blur="$refs.dateContext.hide()"
      @input="
        ;[setCopyFromDateString(dateString, 'dateString'), delayedUpdate(copy)]
      "
      @keydown.enter="delayedUpdate(copy, true)"
    />
    <Context
      ref="dateContext"
      :hide-on-click-outside="false"
      class="datepicker-context"
    >
      <client-only>
        <date-picker
          :inline="true"
          :monday-first="true"
          :use-utc="true"
          :value="dateObject"
          class="datepicker"
          @input=";[setCopy($event, 'dateObject'), delayedUpdate(copy, true)]"
        ></date-picker>
      </client-only>
    </Context>
  </div>
</template>

<script>
import moment from 'moment'

import {
  getDateMomentFormat,
  getDateHumanReadableFormat,
} from '@baserow/modules/database/utils/date'
import filterTypeInput from '@baserow/modules/database/mixins/filterTypeInput'

export default {
  name: 'ViewFilterTypeDate',
  mixins: [filterTypeInput],
  props: {
    value: {
      type: String,
      required: true,
    },
    fieldId: {
      type: Number,
      required: true,
    },
    primary: {
      type: Object,
      required: true,
    },
    fields: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      copy: '',
      dateString: '',
      dateObject: '',
    }
  },
  computed: {
    field() {
      return this.primary.id === this.fieldId
        ? this.primary
        : this.fields.find((f) => f.id === this.fieldId)
    },
  },
  watch: {
    value(value) {
      this.setCopy(value)
    },
  },
  created() {
    this.setCopy(this.value)
  },
  mounted() {
    this.$v.$touch()
  },
  methods: {
    setCopy(value, sender) {
      const newDate = moment.utc(value)

      if (newDate.isValid()) {
        this.copy = newDate.format('YYYY-MM-DD')

        if (sender !== 'dateObject') {
          this.dateObject = newDate.toDate()
        }

        if (sender !== 'dateString') {
          const dateFormat = getDateMomentFormat(this.field.date_format)
          this.dateString = newDate.format(dateFormat)
        }
      }
    },
    setCopyFromDateString(value, sender) {
      if (value === '') {
        this.copy = ''
        return
      }

      const dateFormat = getDateMomentFormat(this.field.date_format)
      const newDate = moment.utc(value, dateFormat)

      if (newDate.isValid()) {
        this.setCopy(newDate, sender)
      } else {
        this.copy = value
      }
    },
    getDatePlaceholder(field) {
      return getDateHumanReadableFormat(field.date_format)
    },
    focus() {
      this.$refs.date.focus()
    },
  },
  validations: {
    copy: {
      date(value) {
        return value === '' || moment(value).isValid()
      },
    },
  },
}
</script>
