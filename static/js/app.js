var newApp = angular.module('newApp',[],function($interpolateProvider){
    $interpolateProvider.startSymbol("[[");
    $interpolateProvider.endSymbol("]]");
});

newApp.controller("MainController",['$scope','$http','$window', function($scope,$http,$window){
    // $scope.test_var = "testing scope";
    // $scope.changeText = function(){
    //     $('#testVarH2').text("changed text");

    $scope.tasks = $window.his_tasks;
    $scope.input_url = null;
    $scope.filename = null;
    $scope.loginForm = function(){
        $http({
            url: '/login',
            method: 'POST',
            data: JSON.stringify({
                'username':$scope.login.username,
                'password':$scope.login.password
            }),
            headers: {'Content-Type':'application/json'}
        }).then(function(response){

            if(response.data['status'] == true){
                $window.location.reload();
            }
            else{

            }
        });
    }

    $scope.signupForm = function(){
        
        $http({
            url: '/signup',
            method: 'POST',
            data: JSON.stringify({
                'username':$scope.signup.username,
                'password':$scope.signup.password
            }),
            headers: {'Content-Type':'application/json'}
        }).then(function(response){


            if(response.data['status'] == true){
                $window.location.reload();
            }
            else{

            }

        });
    }


    $scope.scrapForm = function(){
            
            $http({
                url: '/crawl',
                method: 'POST',
                data: JSON.stringify({
                    'scrap':$scope.scrapModel,
                    }),
                headers: {'Content-Type':'application/json'}
            }).then(function(response){


                if(response.data['status'] == true){
                    $scope.input_url = response.data.url;
                    $scope.filename = response.data.filename;
                }
                else{

                }

            });
        }

    $scope.downloadFile = function(filename){
        $window.location.href = "/download?filename="+filename;
    }






}]);