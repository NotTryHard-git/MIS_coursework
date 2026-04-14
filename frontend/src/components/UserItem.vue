<script >
export default {
  props: {
    data: {
      type: Object
    }
  },
  data(){
    return{
      state1: 0
    }
  }
}
</script>
<template>
<div class="d-flex flex-column align-items-center" style="width: 200px; padding: 30px; margin: 40px;">
    <!-- Иконка человечка -->
    <div class="bg-secondary bg-opacity-10 rounded-circle p-3 mb-2">
        <i class="fas fa-user fa-2x text-secondary"></i>
    </div>
    
    <!-- Плашка с информацией -->
    <div class="card text-center w-100" style="background-color: #f8f9fa;">
        <div class="card-body p-2">
            <div class="fw-bold text-warning small">{{this.data.login}}</div>
            <div class="small text-muted" style="font-size: 0.75rem;">{{this.data.last_name +' '+this.data.first_name[0] +'. '+ this.data.middle_name[0]+'.' }}</div>
        </div>
    </div>
</div>
</template>

<style scoped></style>