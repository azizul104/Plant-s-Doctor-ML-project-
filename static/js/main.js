// $(document).ready(function() {
//   $('#submit-id').click(function() {
//       var form_data = new FormData($('#upload-file')[0]);
//       $.ajax({
//           type: 'POST',
//           url: '/apple-predict',
//           data: form_data,
//           contentType: false,
//           cache: false,
//           processData: false,
//           success: function(data) {
//               console.log('Success!');
//           },
//       })
//       .done(function(data) {
//           $('#show-id').text(data.name).show();           
//           });
//   });
// });