<script>
import Footer from '@/components/Footer.vue';
import Header from '@/components/Header.vue';
import AdminCatalog from '@/components/AdminCatalog.vue';

export default {
    components:{
        Header,
        Footer,
        AdminCatalog
    },
  data(){
    return{
      state1: 0
    }
  }
}
</script>
<template>
   <Header></Header>
   <AdminCatalog></AdminCatalog>
    <Footer></Footer>
</template>
<style scoped>
</style>